# nn_sinterf_autoneuralnet.py
#
# Automatic Neural Network Modelling Pipeline
# From MML Library by Nathmath

import numpy as np
try:
    import torch
except ImportError:
    torch = None

import math
import pandas as pd
from copy import deepcopy
from typing import Any, List, Dict, Tuple, Literal, Optional, Sequence

from .objtyp import Object
from .tensor import Tensor

from .baseml import MLBase
from .baseml import Regression, Classification

from .nn_base import nn_Base
from .nn_module import nn_Module

from .nn import RNN, LSTM
from .nn import RMSE, BCE, MCE, AdamW
from .nn import ReLU, LeakyReLU, GELU, Softplus, Tanh, Sigmoid, Softmax
from .nn import nn_auto_AutoMLP, nn_auto_AutoTMS

from .nn import nn_SInterf_Evaluator


# Automatic Neural Network Modeller
class nn_SInterf_AutoNeuralNetwork(nn_Module, Regression, Classification):
    """
    Neural Network Simple Interface - Automatic Neural Network.
    
    A high‑level dynamic neural-network builder for the MML framework.
    It automatically create a neural network and wires it into an Evaluator 
    instance based on the user-supplied task, data and hyper-knobs.
    It depends on internal network builders, like:
        nn_AutoMLP, nn_AutoLSTM, etc...
    
    Tasks supported  : 
        "reg": Regression, with linear output, may use MSE/RMSE/MAE as criterion,
        "bin-cls": Binary Classification, with Sigmoid activated output, 
            may use BinaryCrossEntropy as criterion,
        "mul-cls": Multiple Classification, with raw logits output
            (Softmax will be applied in MultiCrossEntropy), may use MultiCrossEntropy as criterion,
        "encoder-decoder": Encoder-Decoder arch, with restored input as output, 
            in general, a regression task, so use MSE/RMSE/MAE as criterion,
    Model arch       :
        AutoMLP             - Pure MLP layers with dropout and activation
        AutoTMS             - Recurrent based modules and then MLP layers
    Data description : 
        "tabular" (MLP)     - Tabular data, use AutoMLP arch to deal with the task
        "ts" (TMS)          - Time Series data, use AutoTMS to deal with the task
    Key hyper-params :                                          
        hidden      - hidden layer dimensions, must be a sequence of int
        parameters  - log10 of total params, budget around 10^k    
        task        - task name of your work, supported as described above
        arch        - architecture you prefer, supported as described above
        des         - describe your data as `tabular` or `ts`
        dropout     - per-layer dropout rate (0-1, default 0.2)      
        memoryless  - if True, hidden width never grows layer-wise  
    """
    
    __attr__ = "MML.nn_SInterf_AutoNeuralNetwork"
    
    @staticmethod
    def _ceil_pow_two(x: int) -> int:
        """
        Return the next power-of-two >= x (used to keep sizes tidy).
        
        Returns:
            The smallest power of two that is greater than or equal to x.

        Raises:
            ValueError: If x is not a positive integer.

        E.g. input 4 -> next power of 2 is 2^2 = 4
        E.g. inpur 10 -> next power of 2 is 2^4 = 16
        """
        if x <= 0:
            raise ValueError(f"_ceil_pow_two() only accepts positive values")
        return 1 if x <= 1 else 2 ** math.ceil(math.log2(x))
    
    @staticmethod
    def _infer_io_dims(X: Tensor, y: Tensor, task: str) -> Tuple[int, int]:
        """
        Infer input_dim and output_dim from data tensors.
        
        Args:
            X: Tensor, Input tensor with at least 2 dimensions. The last dimension represents the input features.
            y: Tensor, Target tensor with at least 2 dimensions. The last dimension represents the target values/classes.
            task (str): Task type in string. Currently, we support: "reg", "bin-cls", "mul-cls", or "encoder-decoder".

        Returns:
            Tuple[int, int]: (input_dim, output_dim)
                A tuple containing the input dimension and output dimension.

        Raises:
            ValueError: If X or y are not MML Tensors
            ValueError: If X or y has fewer than 2 dimensions
            ValueError: If the task name is unsupported or unknown.
        """
        
        # Input check and type check
        if isinstance(X, Tensor) == False:
            raise ValueError(f"In AutoNN's _infer_io_dims(), input `X` must be in a MML `Tensor` format but you have {type(X)}")
        if isinstance(y, Tensor) == False:
            raise ValueError(f"In AutoNN's _infer_io_dims(), input `y` must be in a MML `Tensor` format but you have {type(y)}")
            
        # Input dimension check - X and y must be at least 2 dimensions
        if len(X.shape) < 2:
            raise ValueError(f"In AutoNN's _infer_io_dims(), input `X` must be in a MML `Tensor` having at least 2 dimensions like [Batch, ..., Features], but you have {X.shape}")
        if len(y.shape) < 2:
            raise ValueError(f"In AutoNN's _infer_io_dims(), input `y` must be in a MML `Tensor` having at least 2 dimensions like [Batch, ..., Targets], but you have {y.shape}")
        
        # Author: NathMATH and DOF Studio
        input_dim = X.shape[-1]  # for both [N, F] and [N, T, F] and [N, ..., F] formats
    
        # In current implementation, we support:
        # reg, bin-cls, mul-cls, encoder-decoder
        if task == "reg":
            output_dim = y.shape[-1]
        elif task == "bin-cls":
            output_dim = 1
        elif task == "mul-cls":
            output_dim = y.shape[-1]
        elif task == "encoder-decoder":
            output_dim = y.shape[-1]
        else:
            raise ValueError(f"Unknown or unsupported task {task}")
    
        return input_dim, output_dim
    
    @staticmethod
    def _infer_hidden_shapes(in_features: int, 
                             out_features: int,
                             log10_params: float,
                             task: str,
                             arch: str,
                             *, 
                             max_layers: int = 6,
                             memoryless: bool = False,
                             **kwargs) -> List[int]:
        """
        Infer hidden layer widths so total trainable parameters ~= 10 ** log10_params.
        A very rough heuristic: we allocate at most max_layers.
        Semantics for auto-encoders: this archtecture is only for encoder layers.
        
        Different behaviors in two archs:
            MLP Arch: All hidden layers are Dense layers with activations and probably dropouts.
            TMS Arch: The 1st hidden layer is stacked recurrent modules and rest are Dense layers.
            
        Args:
            in_features: int, Number of input features.
            out_features: int, Number of output features.
            log10_params: float, Log base-10 of the target number of trainable parameters.
            task: str, Task type in string. Currently, we support: "reg", "bin-cls", "mul-cls", or "encoder-decoder".
            arch: str, Architecture type in string. Can be either "MLP" or "TMS".
            max_layers: int, Maximum number of hidden layers to consider (default is 6).
            memoryless: int, If True, use a memoryless funnel architecture. Otherwise, use a zoom-in/zoom-out architecture (default is False).

        Returns:
            List[int]: A list containing the widths of the inferred hidden layers.  An empty list indicates no hidden layers are needed.

        Raises:
            ValueError: If task is not one of "reg", "bin-cls", "mul-cls", or "encoder-decoder".
            ValueError: If arch is not one of "MLP" or "TMS".
            ValueError: When using TMS arch, parameter number (10**log10_params) is too small and left no hidden layers. TMS arch must contain at least one hidden layer for recurrent blocks.

        """       
        
        # Normalize task
        task = task.lower()
        if task not in {"reg", "bin-cls", "mul-cls", "encoder-decoder"}:
            raise ValueError(f'Invalid `task` input, it must in ("reg", "bin-cls", "mul-cls", "encoder-decoder") but got {task}')
        
        # Normalize arch
        arch = arch.upper()
        if arch not in {"MLP", "TMS"}:
            raise ValueError(f'Invalid `arch` input, it must in ("MLP", "TMS") but got {arch}')
        
        # Target parameter number: 10^n
        target = int(10 ** log10_params)
        
        # Minimum params: no hidden
        # If target is less than minimum, then 
        min_params = in_features * out_features + out_features
        if target <= min_params:
            # If MLP architecture, that's okay
            if arch == "MLP":
                return []
            # Else if Time Series architecture, that's prohihited, raise ValueError
            elif arch == "TMS":
                raise ValueError(f"In AutoNN's _infer_hidden_shapes(), when using TMS arch, parameter number (10**{log10_params} = {target}) is too small and left no hidden layers. TMS arch must contain at least one hidden layer for recurrent blocks.")
                
        def _ceil_pow_two(x: int) -> int:      # convenience wrapper
           return nn_SInterf_AutoNeuralNetwork._ceil_pow_two(max(1, x))

        def _floor_pow_two(x: int) -> int:
           return 1 if x <= 1 else 1 << (x.bit_length() - 1)
        
        # Helpers to evaluate total parameters having in one architecture
        def _param_count(first: int, hiddens: List[int]) -> int:
            """
            Module params (+2x on first layer for TMS recurrent blocks).
            """
            total, prev = 0, first
            for i, h in enumerate(hiddens):
                mult = 2 if (i == 0 and arch == "TMS") else 1
                total += mult * (prev * h + h)
                prev = h
            total += prev * out_features + out_features
            return total

        best_gap = float("inf")
        best_hidden = []

        # MEMORY-LESS - strict funnel (monotone decrease)
        if memoryless:
            
            # Search shrink‑ratios r from 0.20 to 0.95 in 0.05 steps
            for r_step in range(8, 40):
                r = 0.025 * r_step
                widths, prev = [], in_features

                for _ in range(max_layers):
                    # Round to the nearest 4 divisible number
                    nxt = int(round(prev * r / 4)) * 4
                    if nxt <= out_features or nxt >= prev:
                        break
                    widths.append(nxt)
                    prev = nxt

                if not widths:
                    continue

                gap = abs(_param_count(in_features, widths) - target)
                if gap < best_gap:
                    best_gap, best_hidden = gap, widths

            return best_hidden

        # MEMORY‑ABLE - zoom-in, then zoom-out (one peak)
        else:
            
            # Iterate layer by layer
            for n_up in range(1, max_layers):                 # at least one grow
                
                for up_ratio in (2.0, 1.7, 1.3, 2.5, 2.1, 1.25, 1.1):
                    grow, prev = [], in_features

                    # Ascending phase
                    for _ in range(n_up):
                        nxt = max(prev + 4, int(round(prev * up_ratio / 4)) * 4)
                        grow.append(nxt)
                        prev = nxt
                        # Leave enough room to fall
                        if len(grow) >= max_layers / 4:
                            break

                    peak = grow[-1]
                    if peak <= in_features:                  # must really grow
                        continue

                    # Descending phase
                    for down_ratio in (0.5, 0.364, 0.167, 0.7, 0.33, 0.75, 0.25):
                        widths = grow.copy()
                        prev_d = peak
                        while len(widths) < max_layers:
                            nxt = int(round(prev_d * down_ratio / 4)) * 4
                            if nxt <= out_features or nxt >= prev_d:
                                break
                            widths.append(nxt)
                            prev_d = nxt

                        if len(widths) <= len(grow):         # no descent
                            continue

                        gap = abs(_param_count(in_features, widths) - target)
                        if gap < best_gap:
                            best_gap, best_hidden = gap, widths

        return best_hidden

    def __init__(self,
                 X: Tensor | int, 
                 y: Tensor | int,
                 task: Literal["reg", "bin-cls", "mul-cls", "encoder-decoder"] = "reg",
                 des: Literal["tabular", "ts"] = "tabular",
                 log10_params: float = 3.667,
                 max_layers: int = 6,
                 memoryless: bool = True,
                 *,
                 lr: float = 1e-3,
                 hidden: Sequence[int] | None = None,
                 actv: type = Tanh,
                 init_scale: float = 0.1,
                 dropout: float = 0, 
                 module_name: str = "nn_SInterf_AutoNeuralNetwork",
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        Initializes the Auto Neural Net module.

        Args:
            X: Tensor | int, Input data Tensor, used to derive input features. If given int, then regarded as input dimension.
            y: Tensor | int, Target data Tensor, used to derive output_features. If given int, then regarded as input dimension.
            task: Literal["reg", "bin-cls", "mul-cls", "encoder-decoder"]. Defaults to "reg".
            des: Literal["tabular", "ts"]. Defaults to "tabular".
            log10_params: float, Log base-10 of the target number of trainable parameters. Defaults to 3.667.
            max_layers: int, Maximum number of hidden layers to consider. Defaults to 6.
            memoryless, bool, If True, use a memoryless funnel architecture. 
                    Otherwise, use a zoom-in/zoom-out architecture. Defaults to True.
            lr: float, Learning rate for the optimizer. Defaults to 1e-3.
            hidden: Sequence[int] | None, optional, Sequence of hidden layer widths. 
                    If None, layers are inferred automatically. 
                    If non-None, we will use the hidden scheme provided instead of log10_params to infer.
                    Defaults to None.
            actv: type, Activation function to use in hidden layers. Defaults to Tanh.
            init_scale: float, Initial scale for the weights. Defaults to 0.1.
            dropout: float, Dropout rate in some selected layers. Defaults to 0.
            module_name: str, Name of the module. Defaults to "nn_SInterf_AutoNeuralNetwork".
            backend: Literal["torch", "numpy"], Backend for Tensors, can be ("torch" or "numpy"). Defaults to "torch".
            dtype: type | str, Data type to use. Defaults to None.
            device: str, Description of device to use ("cpu" or "cuda"). Defaults to None.
            autograd: bool, Whether to enable Torch's autograd. Defaults to False.
            **kwargs: Additional args for compatibility, passed to Auto*** module, optimizer, criterion, evaluator.

        Raises:
            ValueError: If task is not one of "reg", "bin-cls", "mul-cls", or "encoder-decoder".
            ValueError: If des is not one of "tabular", "ts".
            ValueError: If input tensors X and y are not in MML Tensor format.
            ValueError: If input tensors X and y have fewer than 2 dimensions.
            ValueError: When using TMS arch (ts des), parameter number (10**log10_params) is too small and left no hidden layers. TMS arch must contain at least one hidden layer for recurrent blocks.
        """
        
        # Normalize task
        task = task.lower()
        if task not in {"reg", "bin-cls", "mul-cls", "encoder-decoder"}:
            raise ValueError(f'Invalid `task` input, it must in ("reg", "bin-cls", "mul-cls", "encoder-decoder") but got {task}')
        
        # Normalize des
        des = des.lower()
        if des not in {"tabular", "ts"}:
            raise ValueError(f'Invalid `des` input, it must in ("tabular", "ts") but got {des}')
        
        # Input check and type check
        if type(X) != type(y):
            raise ValueError(f"In AutoNN's __init__, input `X` and `y` must have the same type, a data Tensor or int indicating dimensions. But got X: {type(X)}, y: {type(y)}")
        if isinstance(X, Tensor) == False and isinstance(X, int) == False:
            raise ValueError(f"In AutoNN's __init__(), input `X` must be in a MML `Tensor` format or an int indicating dimension, but you have {type(X)}")
        if isinstance(y, Tensor) == False and isinstance(y, int) == False:
            raise ValueError(f"In AutoNN's __init__(), input `y` must be in a MML `Tensor` format or an int indicating dimension, but you have {type(y)}")
            
        # Input dimension check - X and y must be at least 2 dimensions
        if isinstance(X, Tensor):
            if len(X.shape) < 2:
                raise ValueError(f"In AutoNN's __init__(), input `X` must be in a MML `Tensor` having at least 2 dimensions like [Batch, ..., Features], but you have {X.shape}")
        if isinstance(y, Tensor):
            if len(y.shape) < 2:
                raise ValueError(f"In AutoNN's __init__(), input `y` must be in a MML `Tensor` having at least 2 dimensions like [Batch, ..., Targets], but you have {y.shape}")
        
        # Invoke nn_Module
        nn_Module.__init__(self, module_name=module_name, backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
        
        # Record other non-kwargs
        self.reference_X = X if isinstance(X, Tensor) else None
        self.reference_y = y if isinstance(y, Tensor) else None
        self.task = task
        self.des  = des
        self.arch = "MLP" if des == "tabular" else "TMS"
        self.log10_params = log10_params
        self.max_layers = max_layers
        self.memoryless = memoryless

        # Record hidden for re-initialization purposes
        self.hidden = None # place holder, will be evaluated once creating the module

        # Infer and record I/O dims
        if isinstance(X, Tensor) and isinstance(y, Tensor):
            in_dim, out_dim = self._infer_io_dims(self.reference_X, self.reference_y, self.task)
        else:
            in_dim, out_dim = X, y
        self.in_dim = in_dim
        self.out_dim = out_dim
        
        # Record kwargs
        self.lr = lr
        self.actv = actv
        self.init_scale = init_scale
        self.dropout = dropout
        self.module_name = module_name
        self.kwargs = kwargs
        
        # Evaluator placeholders
        module = None
        optm = None
        crit = None

        # Build an AutoMLP module
        if des == "tabular":
            if hidden is None:
                hidden = self._infer_hidden_shapes(in_dim, out_dim, log10_params, task = task, arch = self.arch, max_layers = max_layers, memoryless = memoryless, **kwargs)
            # Record hidden
            self.hidden = hidden
            # Build a module
            module = nn_auto_AutoMLP(in_dim, out_dim, hidden = hidden, task = task, 
                                     actv = actv, has_bias = True, init_scale = init_scale, dropout = dropout,
                                     module_name = module_name + ".module", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
            
        # Build an AutoTMS module
        elif des == "ts":
            if hidden is None:
                hidden = self._infer_hidden_shapes(in_dim, out_dim, log10_params, task = task, arch = self.arch, max_layers = max_layers, memoryless = memoryless, **kwargs)
            # Record hidden
            self.hidden = hidden
            # Build a module
            module = nn_auto_AutoTMS(in_dim, out_dim, hidden = hidden, task = task, 
                                     actv = actv, has_bias = True, init_scale = init_scale, dropout = dropout,
                                     module_name = module_name + ".module", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)

        # Build Loss and Optimizer
        if task == "reg":
            crit = RMSE(module_name = module_name + ".crit", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        elif task == "bin-cls":
            crit = BCE(module_name = module_name + ".crit", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        elif task == "mul-cls":
            crit = MCE(module_name = module_name + ".crit", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        elif task == "encoder-decoder":
            crit = RMSE(module_name = module_name + ".crit", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        optm = AdamW(module.parameters(), lr = lr, module_name = module_name + ".optm", backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)

            
        # Build the Evaluator
        eval_task = None
        if task in {"reg", "encoder-decoder"}:
            eval_task = "regression"
        elif task in {"bin-cls", "mul-cls"}:
            eval_task = "classification"
        evaluator = nn_SInterf_Evaluator(name = module_name + ".evaluator", task = eval_task,
                                         module = module, criterion = crit, optimizer = optm, **kwargs)
        # Record and save the evaluator
        self.evaluator = evaluator

    def _renew_module_pipeline(self, *, make_sure: bool = False, **kwargs):
        """
        Renew the entire module pipeline by:
            1. re-initializing the module
            2. re-initializing the optimizer
            3. re-initializing the loss function
            4. re-initializing the evaluator        

        Returns:
            ----------
            self
            
        Raises:
            ----------
            ValueError: if called this function with `make_sure` False
        """
        # If make_sure != True, raise ValueError
        if make_sure != True:
            raise ValueError("Pay attention! You are calling _renew_module_pipeline() which will completely renew the model and related evaluator. But you did not pass `make_sure` to True. Renewing is surpressed. Please double check your intention.")
            
        # Rebuild everything similar to __init__
        
        # Evaluator placeholders
        module = None
        optm = None
        crit = None

        # Build an AutoMLP module
        if self.arch == "MLP":
            module = nn_auto_AutoMLP(self.in_dim, self.out_dim, hidden = self.hidden, task = self.task, 
                                     actv = self.actv, has_bias = True, init_scale = self.init_scale, dropout = self.dropout,
                                     module_name = self.module_name + ".module", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)
        # Build an AutoTMS module
        elif self.arch == "TMS":
            module = nn_auto_AutoTMS(self.in_dim, self.out_dim, hidden = self.hidden, task = self.task, 
                                     actv = self.actv, has_bias = True, init_scale = self.init_scale, dropout = self.dropout,
                                     module_name = self.module_name + ".module", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)

        # Build Loss and Optimizer
        if self.task == "reg":
            crit = RMSE(module_name = self.module_name + ".crit", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)
        elif self.task == "bin-cls":
            crit = BCE(module_name = self.module_name + ".crit", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)
        elif self.task == "mul-cls":
            crit = MCE(module_name = self.module_name + ".crit", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)
        elif self.task == "encoder-decoder":
            crit = RMSE(module_name = self.module_name + ".crit", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)
        optm = AdamW(module.parameters(), lr = self.lr, module_name = self.module_name + ".optm", backend = self.backend, dtype = self.dtype, device = self.device, autograd = self.autograd, **self.kwargs)

        # Build the Evaluator
        eval_task = None
        if self.task in {"reg", "encoder-decoder"}:
            eval_task = "regression"
        elif self.task in {"bin-cls", "mul-cls"}:
            eval_task = "classification"
        evaluator = nn_SInterf_Evaluator(name = self.module_name + ".evaluator", task = eval_task,
                                         module = module, criterion = crit, optimizer = optm, **self.kwargs)
        # Record and save the evaluator
        self.evaluator = evaluator
        
        return self

    def fit(self, 
            X: Tensor, 
            y: Tensor,
            epoches: int = 100,
            batch_size: int | None = None,
            shuffle: bool = True,
            random_state: int | None = None,
            to_device: str | None = None,
            *,
            one_hot: bool = True,
            verbosity: int | None = None,
            evalper: int = 1,
            evalset: Dict[str, Tuple[Tensor, Tensor]] | None = None,
            evalmetrics: List[str] | str | None = None,
            early_stop: int | None = None,
            early_stop_logic: str = "some",
            continue_to_train: bool | None = True,
            **kwargs):
        """
        Train neural network module defined in `self.evaluator.module` for at most `epoches` epoches with evaluation. 
        In this AutoNN wrapper, we do the following things:
            1. Record and renew the new training data and dimensions
            2. If renew the module, then renew the module
            3. Call evaluator to train the module with the data
        
        Evaluation Remark:
            ----------
            You may want to evaluate datasets while training. If so, please do the following things:
                1. set `verbosity` = 1 to print the evaluation
                2. set the `evalset` to a dict of tuples of your dataset that is going to be evaluated
                3. set the `evalmetrics` either to a string of metrics or a list of strings
            You may want the algorithm to decide to stop training automatically. If so, please do things above, plus:
                1. set `early_stop` to a number of batches, like 1 or 2, which acts like: 
                    if the metrics for all/some/any/most of the evaluation sets do not decrease anymore, 
                    the training process will be terminated and return
                2. set `early_stop_logic` to determine the way of processing non-decreasing datasets/metrics
                3. If you hope to continue to train again, call this `fit` again with `continue_to_train` set to True

        Parameters:
            ----------
            X: Tensor, the feature tensor (the 1st dimension is sample).
            y: Tensor, the target values (for regression, numerical; for classification, one-hot or multi-label).
            epoches: int, the number of rounds (maximum rounds) to be trainned. Default is 100.
            batch_size: int, the number of samples trained each time. Must be greater than 1. If None, then use all.
            shuffle: bool, whether data will be shuffled for each round (same device same type). By default, True (if batch_size is None then omitted).
            random_seed: int | None, the random seed set to perform shuffle, can be None which means to randomly choose one.
            Optional:
                one_hot : bool, if y is one-hot encoded for classification tasks.
                verbosity: int | None, if >= 1 and having `evalset`, then will report metrics each batch.
                evalper: int, the number of rounds to perform before evaluation conducted again.
                evalset: Dict[name : Tuple[X, y],
                              ...], | None, if provided, it may be used as evaluation set. XGBoost style.
                evalmetrics: list of str | str | None, metrics used to do the evaluation. Will be printed.
                early_stop: int | None, if non-None, then if metrics NOT gained for `early_stop` times, the forest will stop training.
                early_stop_logic: str, the logic when deciding on multiple metrics, can be {"any", "some", "most", "all"}.
                continue_to_train: bool | None, if non-None and True, the machine will try to restore the place it was and continue
                                   to train new estimators until a new stopping criterion meets or until reaches the max number of allowed estimators.
                
        Returns:
            ----------
            self
        """
        #######################################################################
        # Pre checks
        #######################################################################
        
        # Type Check (must be an Tensor type).
        if isinstance(X, Tensor) == False or isinstance(y, Tensor) == False:
            raise ValueError("Input dataset must be Tensor for neural networks. Use Tensor(data) or Tensor(data) to convert.")
        if type(X) != type(y):
            raise ValueError("Input feature `X` and target `y` must have the same type, use Tensor instead.")
        
        # Dimension Check.
        if len(X.shape) < 2:
            raise ValueError("Input feature `X` must be at least 2 dimensional (the first is for samples).")
        if len(y.shape) == 1:
            raise ValueError("Input target `y` must also be a 2d data. If only one label or value, use data.reshape([-1, 1])")
                    
        # Batch size Check.
        if batch_size is not None:
            if int(batch_size) < 1:
                raise ValueError("Input `batch_size` must be an interger which is greater or equal to 1.")
                        
        # Stopping Logic Check.
        if early_stop_logic not in ("any", "some", "most", "all"):
            raise ValueError("Stopping logic `early_stop_logic` must be one of ('any', 'some', 'most', 'all')")

        # Record a reference of new data
        self.reference_X = X
        self.reference_y = y

        # Infer and record I/O dims
        in_dim, out_dim = self._infer_io_dims(self.reference_X, self.reference_y, self.task)
        self.in_dim = in_dim
        self.out_dim = out_dim
        
        # If renew the module, then renew it
        if continue_to_train == False:
            self._renew_module_pipeline(make_sure = not continue_to_train)
        
        # Call evaluator to train
        self.evaluator.fit(X, y, 
                           epoches = epoches, batch_size = batch_size, shuffle = shuffle, random_state = random_state,
                           to_device = to_device, one_hot = one_hot, verbosity = verbosity, 
                           evalper = evalper, evalset = evalset, evalmetrics = evalmetrics, 
                           early_stop = early_stop, early_stop_logic = early_stop_logic, continue_to_train = None,
                           **kwargs)
        return self

    def fit_metrics(self, 
                    metric: str | None = None,
                    collect: Sequence[str] | None = None,
                    **kwargs) -> Tuple[dict, pd.DataFrame]:
        """
        Extracts and returns evaluation metrics from the evaluator's history (per {evalper} epoches).

        Args:
            metric: str | None, Metric to extract. If None, uses the first available metric. Defaults to None.
            collect: Sequence[str] | None, Evaluation sets to collect (e.g., "train", "val"). 
                     If None, collects metrics from all evaluation sets. Defaults to None.
            **kwargs: Additional keyword arguments passed to pandas DataFrame constructor.

        Returns:
            Tuple[dict, pd.DataFrame]: A tuple containing:
                - evaldict (dict): A dictionary where keys are evaluation set names and values are lists of metric values for each epoch/iteration. Also contains "No" key representing the iteration number.
                - df (pd.DataFrame): A pandas DataFrame constructed from the `evaldict`.

        Raises:
            ValueError: If no training evaluation history is found in the evaluator.
            ValueError: If the specified metric is not found in the evaluation history.
            ValueError: If any of the requested evaluation sets are not found in the history.
        """

        # If metric is left None, then use the first metric
        if len(self.evaluator.evalhist_) == 0:
            raise ValueError(f"No training evaluation history found in evaluator {print(self.evaluator)}. Please first train the model by calling .fit()")
        
        # Get a copy of the evaluation hist{No: {Set: {Metric: Value, ...}, ...}, ...}
        evalhist = deepcopy(self.evaluator.evalhist_)
        
        # Prepare some data for checking
        sets = evalhist[list(evalhist.keys())[0]]
        metrics = sets[list(sets.keys())[0]]
        
        # If metric retained None, select the 1st matric
        if metric is None:
            metric = list(metrics.keys())[0]
        else:
            if metric not in list(metrics.keys()):
                raise ValueError(f"Invalid arg `metric` = {metric}. No matched metrics found. Found {list(metrics.keys())}")
        
        # If collect (sets) retained None, select all
        if collect is None:
            collect = list(sets.keys())
        else:
            skeys = list(sets.keys())
            for col in collect:
                if col not in skeys():
                    raise ValueError(f"Invalid arg `collect` = {collect}. Unmatched evaluation set name ({col}) found. You have ({skeys}) elements to choose from")
        
        # Extract keys once
        keys = list(evalhist.keys())
        
        # Create the evaluation dictionary using a dictionary comprehension
        evaldict: Dict[Any, List[Any]] = {
            "No": keys,
            **{c: np.stack([evalhist[k][c][metric].to_list() for k in keys]) for c in collect}
        }
            
        return evaldict, pd.DataFrame(evaldict, **kwargs)

    def predict(self, X: Tensor, **kwargs) -> Tensor:
        """
        Predict target values for samples in X in batches.
        In this AutoNN wrapper, we call self.evaluator to do the prediction.
        
        Returns:
            Tensor, output of predictions.
            
        Raises:
            ValueError: if X is not an instance of MML.Tensor.
            Errors checked in Evaluator.
        """
        # Type Check (must be an Tensor type).
        if isinstance(X, Tensor) == False:
            raise ValueError("Input dataset must be a Tensor. Use Tensor(data) to convert.")
        
        self.evaluator.eval()
        return self.evaluator.predict(X, **kwargs)

    def predict_loss(self, X: Tensor, y: Tensor, **kwargs) -> Tuple[Tensor, Tensor]:
        """
        Predict target values for samples in X and calculate the loss by a given target y.
        In this AutoNN wrapper, we call self.evaluator to do the prediction.
        
        Returns:
            Tuple[Tensor, Tensor]: output of predictions, loss.
            
        Raises:
            ValueError: if X or y is not an instance of MML.Tensor.
            Errors checked in Evaluator.
        """
        # Type Check (must be an Tensor type).
        if isinstance(X, Tensor) == False or isinstance(y, Tensor) == False:
            raise ValueError("Input dataset must be a Tensor. Use Tensor(data) to convert.")
        
        self.evaluator.eval()
        return self.evaluator.predict_loss(X, y, **kwargs)
    
    def predict_encoder(self, X: Tensor, **kwargs) -> Tensor:
        """
        Predict auto-encoder dimension reducted values for samples in X in batches.
        Note, this function may work in two modes:
            1. If the self.module has an attribute of `forward_encoder`, then call this to 
                calculate the hidden states with respect to the inputs
            2. Otherwise, falls back to normal predict().
        In this AutoNN wrapper, we call self.evaluator to do the prediction.
        
        Returns:
            Tensor, output of hidden states (or just the output if not having a forward_encoder attribute).
            
        Raises:
            ValueError: if X is not an instance of MML.Tensor.
            Errors checked in Evaluator.
        """
        # Type Check (must be an Tensor type).
        if isinstance(X, Tensor) == False:
            raise ValueError("Input dataset must be a Tensor. Use Tensor(data) to convert.")
    
        self.evaluator.eval()
        return self.evaluator.predict_encoder(X, **kwargs)
        
    def __repr__(self):
        return f"Auto Neural Network Interface(AutoNN: name = {self.name}, task = {self.task}, des = {self.des}, module = {self.evaluator.module}; has trained n_epoch = {self.evaluator.n_epoch}, n_step = {self.evaluator.n_step})."
    

# Alias for nn_SInterf_AutoNeuralNetwork
AutoNN = nn_SInterf_AutoNeuralNetwork
AutoNeuralNet = nn_SInterf_AutoNeuralNetwork


# Tests for AutoNN with MLP tasks
def test_autonn_mlp():

    import pandas as pd
    from mml import Tensor
    from mml import Classification as Cl
    from mml import RMSE, BinaryCrossEntropy
    from mml import AdamW
    from mml import Evaluator
    
    # This is just an non-rigorous example - 
    
    # Import a sample stock index prediction data
    data = pd.read_csv(
        "https://raw.githubusercontent.com/dof-studio/dtafina/refs/heads/main/MachineLearning/spx-choice-daily-2005-simple.csv")
    data = data.drop(["Date"],axis=1)
    data = data.astype(float)
    
    # Convert to features and targets
    X = Tensor(data.drop(["Next Day"], axis=1).to_numpy(),
               backend="torch", device="cuda", dtype=torch.float32)
    y = Tensor((data[["Next Day"]]).to_numpy(), 
               backend="torch", device="cuda", dtype=torch.float32)
    
    # Standardization to X[4:8]
    X[:, 4:8] = X[:, 4:8] / 1000
    
    # Standardization to all
    X *= 10
    
    # We select some data while next day is 1
    pos_idx = y.flatten().data == 1
    X_pos = X[pos_idx]
    y_pos = y[pos_idx]
    
    # First we construct an AutoEncoder
    autoencoder = AutoNN(12, 8, task="encoder-decoder", des="tabular", hidden=[48,64],
                      dropout=0.2,
                      backend="torch", device="cuda", dtype=torch.float32)
    
    # Then, we define a classifier
    classifier = AutoNN(24, 1, task="bin-cls", des="tabular", hidden = [32, 8],
                      dropout=0.2,
                      backend="torch", device="cuda", dtype=torch.float32)
    
    ######
    # Train the AutoEncoder on positive data
    autoencoder.fit(X_pos, X_pos, 10000,
                    batch_size=None,
                    verbosity=1,
                    evalset={"Train": (X_pos, X_pos)},
                    evalmetrics=["mse", "rmse"])
    
    # Conduct the forward for all data and get residuals
    X_res = autoencoder.predict(X)
    X_dif = X - X_res
    
    ######
    # Train the classifier 
    classifier.fit(X_dif.hstack(X), y, 10000, one_hot=False,
              batch_size=None,
              verbosity=1,
              evalset={"Train": (X_dif.hstack(X), y)},
              evalmetrics=["logloss", "accuracy"])
    
    # Predict results
    y_pred = classifier.predict(X_dif.hstack(X))
    

# Tests for AutoNN with TMS tasks
def test_autonn_tms():
    
    import pandas as pd
    from mml import Tensor
    from mml import Classification as Cl
    from mml import RMSE, BinaryCrossEntropy
    from mml import AdamW
    from mml import Evaluator
    
    # This is just an non-rigorous example - 
    
    # Import a sample stock index prediction data
    data = pd.read_csv(
        "https://raw.githubusercontent.com/dof-studio/dtafina/refs/heads/main/MachineLearning/spx-choice-daily-2005-simple.csv")
    data = data.drop(["Date"],axis=1)
    data = data.astype(float)
    
    # Convert to features and targets
    X = Tensor(data.drop(["Next Day"], axis=1).to_numpy(),
               backend="torch", device="cuda", dtype=torch.float32)
    y = Tensor((data[["Next Day"]]).to_numpy(), 
               backend="torch", device="cuda", dtype=torch.float32)
    
    # Standardization to X[4:8]
    X[:, 4:8] = X[:, 4:8] / 1000
    
    # Standardization to all
    X *= 10
    
    # We create rolling windows
    X, y = Cl.make_rolling_window(X, y, 10)
    
    # We define a classifier
    classifier = AutoNN(X, y, hidden = [32, 16, 8], task="bin-cls", des="ts",
                     recurrent=LSTM, recurrent_layers=1,
                     dropout=0.2,
                     backend="torch", device="cuda", dtype=torch.float32)
    
    ######
    # Train the classifier 
    classifier.fit(X, y, 10000, one_hot=False,
                     batch_size=None,
                     verbosity=1, evalper=1,
                     evalset={"Train": (X, y)},
                     evalmetrics=["logloss", "accuracy"])
    
    # Predict results
    y_pred = classifier.predict(X)
    