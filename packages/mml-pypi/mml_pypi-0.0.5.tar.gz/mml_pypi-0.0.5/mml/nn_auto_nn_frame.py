# nn_auto_nn_frame.py
#
# Automatic Neural Network Construction Framework
# From MML Library by Nathmath

import numpy as np
try:
    import torch
except ImportError:
    torch = None

from typing import List, Sequence, Tuple, Literal, Optional, Any

from copy import deepcopy

from .objtyp import Object
from .tensor import Tensor

from .baseml import MLBase
from .baseml import Regression, Classification

from .nn_base import nn_Base
from .nn_parameter import nn_Parameter
from .nn_module import nn_Module

from .nn import Dense
from .nn import Dropout
from .nn import RNN, LSTM
from .nn import ReLU, LeakyReLU, GELU, Softplus, Tanh, Sigmoid, Softmax


# Implementation of Base Auto Sequential Module
class nn_auto_Sequential(nn_Module):
    """
    Auto-generated Sequential Module.
    
    This is a automatic base module that can be derived to generate a sequential module with inputs, outputs, hidden layers,
    capable of doing regression tasks (reg), binary and multiple classification tasks (bin-cls, mul-cls),
    as well as auto-encoder restoration tasks (encoder-decoder), and so on.
    
    It has basic members, standard architecture, and forward(), forward_encoder() implemenetation.
    For backward(), it simply uses the implementation in nn_BaseModule.
    """
    
    __attr__ = "MML.nn_auto_Sequential"    
    
    def __init__(self, 
                 in_features: int, 
                 out_features: int, 
                 hidden: Sequence[int], 
                 task: str = "any", 
                 actv: type = Tanh,
                 has_bias: bool = True,
                 init_scale: float = 0.1,
                 dropout: float = 0, 
                 *,
                 module_name: str = "nn_auto_Sequential",
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        Automatic Sequential Module Creator.
        Note, we `do not` check task validity and by default passes `any` to be the placeholder.
        In further derived class
        
        Parameters:
            in_features: int, The number of input features for this layer.
            out_features: int, The number of output features for this layer.
            hidden: Sequence of int, The dimension of hidden layers, can be a list of int or tuple of int.
                When in `encoder-decoder` mode, the hidden just shows the `encoder`'s architecture, and the decoder's will
                be automatically built internally and symmetrically.
            task: str, The string name of the task name, we do not check it in the base and passes `any` as a placeholder.
            actv: type, The class of activation function applied to each Dense layer, by default, we use `Tanh`.
            has_bias: bool, A flag indicating whether to include a bias term. Valid values are True or False.
                    If set to True, the layer includes an additive bias term (b). Defaults to True.
            init_scale: float, The scale (maximum number) or weights that are randomly initialized. Defaults to 0.1.
            dropout: float, Dropout rate in some internal dropout layers (must be in [0, 1)). Defaults to 0.            
            
        Optionals:                                                                          
            module_name: str, The name of the module instance. Defaults to "nn_auto_Sequential".
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.in_features: int, The number of input features for this layer.
            self.out_features: int, The number of output features for this layer.
            self.hidden: Sequence of int, Dimensions of hidden layers (encoder only if any).
            self.task: float, The name of task stored, this impacts arch selection and output layer.
            self.actv: type, The class of activation function applied to each Dense layer.
            self.has_bias: bool, A flag indicating whether a bias term is included (True or False).
            self.init_scale: float, A floatting number indicating the maximum value of initial random weights.
            self.dropout: float, A floatting number indicating the dropout rate in the network, can be [0, 1).
            self.backend: Literal["torch", "numpy"], The computational backend used by the layer.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self.n_encoder_modules: int, The number of layers that are encoder layers, used to perform forward_encoder().
            self._modules: Dict[nn_Module], The entire sequential archtecture stored in the module dictionary.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
        
        # Task check (just be a string)
        if isinstance(task, str) == False:
            raise ValueError(f"Argument `task` must be a string type indicating the task performing but you have {task}")
        task = task.lower()
        
        # Dropout rate check (in [0,1))
        if dropout < 0 or dropout >= 1.0:
            raise ValueError(f"Argument `dropout` indicates dropout rate. Must be in [0, 1) but you have {dropout}")
        
        # Record shapes etc
        self.__setattr__("in_features", in_features)
        self.__setattr__("out_features", out_features)
        self.__setattr__("hidden", hidden)
        self.__setattr__("task", task)
        self.__setattr__("actv", actv)
        self.__setattr__("has_bias", has_bias)
        self.__setattr__("init_scale", init_scale)
        self.__setattr__("dropout", dropout)
        
        # Here, set n_encoder_modules as None
        # If used, please set it manually in the derived class
        self.__setattr__("n_encoder_modules", None)
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Compute the module output throughout the entire module (even if an Encoder-Decoder arch).
        This method performs the forward computation for the entire network and outputs the final output,
        note, if you are using an AutoEncoder, this will be outputing the restored data.

        Args:
            x (Tensor): Input tensor of shape (batch_size, in_features, ...) to be transformed by the network.

        Returns:
            Tensor: Output tensor of shape (batch_size, out_features, ...) after applying the entire transformation.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
            ValueError: If the input `x` has a different shape of in_features.
        """
        
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
            
        # Feature check, x's last shape must match in_features
        if x.shape[-1] != self.in_features:
            raise ValueError(f"In performing forward(), input `x` has different feature dimension ({x.shape[-1]}) with `in_features` ({self.in_features})")
        
        # Perform forward layer by layers
        for layer in self._modules.values():
            x = layer(x)
            if isinstance(x, tuple):
                x = x[0]
        
        return x

    def forward_encoder(self, x: Tensor) -> Tensor:
        """
        Compute the module output throughout only the encoder layers (even if a non-Encoder-Decoder arch).
        This method performs the forward computation for only the encoder parts and outputs the hidden state,
        note, if you are using an AutoEncoder, this will be outputing the dimension reducted hidden state.

        Args:
            x (Tensor): Input tensor of shape (batch_size, in_features, ...) to be transformed by the network.

        Returns:
            Tensor: Output tensor of shape (batch_size, out_features, ...) after applying the encoder transformation.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
            ValueError: If the input `x` has a different shape of in_features.
            RuntimeError: If self.n_encoder_modules is None.
            RuntimeError: If the module is in training mode.
        """
        
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward_encoder(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Feature check, x's last shape must match in_features
        if x.shape[-1] != self.in_features:
            raise ValueError(f"In performing forward(), input `x` has different feature dimension ({x.shape[-1]}) with `in_features` ({self.in_features})")
        
        # If self.n_encoder_modules is None
        if self.n_encoder_modules is None:
            raise RuntimeError("In performing forward_encoder(), self.n_encoder_modules is detected to be None. Please check module's compatibility for auto-encoders.")
        
        # We assume auto-encoder is a completely symmetrical structure,
        # so, as recorded, only half of sub-modules are used here.
        
        # Must be in `evaluation` mode
        if self.training == True:
            raise RuntimeError("forward_encoder() is called in `training` mode. It can only be used in `evaluation` mode. Call .eval() first.")
        
        # Perform forward only by encoder layers
        for i, layer in enumerate(self._modules.values()):
            if i < self.n_encoder_modules:
                x = layer(x)
                if isinstance(x, tuple):
                    x = x[0]
            else:
                break

        return x
    
    def __repr__(self):
        return "nn_auto_Sequential(Base Auto Module Class, please derive it)"
       

# Implementation of an Auto MLP Module
class nn_auto_AutoMLP(nn_auto_Sequential):
    """
    Auto-generated MLP (Dense-Dropout-Actv framework) ending with task-specific head.
    
    This is a automatic module that can generate a MLP module with inputs, outputs, hidden layers,
    capable of doing regression tasks (reg), binary and multiple classification tasks (bin-cls, mul-cls),
    as well as auto-encoder restoration tasks (encoder-decoder).
    It servces as a wrapped module providing a complete, auto-generated network structure
    where developpers can use it to create a simple and bench-mark level network in one line.
    """
    
    __attr__ = "MML.nn_auto_AutoMLP"    
    
    def __init__(self, 
                 in_features: int, 
                 out_features: int, 
                 hidden: Sequence[int], 
                 task: Literal["reg", "bin-cls", "mul-cls", "encoder-decoder"] = "reg", 
                 actv: type = Tanh,
                 has_bias: bool = True,
                 init_scale: float = 0.1,
                 dropout: float = 0, 
                 *,
                 module_name: str = "nn_auto_AutoMLP",
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        Automatic MLP Module Creator. It creates an automatic MLP module based on in, out, and hidden.
        Support tasks: 
            "reg": General regression task,
            "bin-cls": Binary Classification task,
            "mul-cls": Multiple Classification task,
            "encoder-decoder": Encoder-Decoder structure restoration task,
            by defualt, it is set to "reg".
        
        Parameters:
            in_features: int, The number of input features for this layer.
            out_features: int, The number of output features for this layer.
            hidden: Sequence of int, The dimension of hidden layers, can be a list of int or tuple of int.
                When in `encoder-decoder` mode, the hidden just shows the `encoder`'s architecture, and the decoder's will
                be automatically built internally and symmetrically.
            task: str, The string name of the task name, can be {"reg", "bin-cls", "mul-cls", "encoder-decoder"}, representing for:
                "reg": Regression, with linear output, may use MSE/RMSE/MAE as criterion,
                "bin-cls": Binary Classification, with Sigmoid activated output, may use BinaryCrossEntropy as criterion,
                "mul-cls": Multiple Classification, with raw logits output (Softmax will be applied in MultiCrossEntropy), may use MultiCrossEntropy as criterion,
                "encoder-decoder": Encoder-Decoder arch, with restored input as output, in general, a regression task, so use MSE/RMSE/MAE as criterion,
            actv: type, The class of activation function applied to each Dense layer, by default, we use `Tanh`.
            has_bias: bool, A flag indicating whether to include a bias term. Valid values are True or False.
                    If set to True, the layer includes an additive bias term (b). Defaults to True.
            init_scale: float, The scale (maximum number) or weights that are randomly initialized. Defaults to 0.1.
            dropout: float, Dropout rate in some internal dropout layers (must be in [0, 1)). Defaults to 0.            
            module_name: str, The name of the module instance. Defaults to "nn_auto_AutoMLP".
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.in_features: int, The number of input features for this layer.
            self.out_features: int, The number of output features for this layer.
            self.hidden: Sequence of int, Dimensions of hidden layers (encoder only if any).
            self.task: float, The name of task stored, this impacts arch selection and output layer.
            self.actv: type, The class of activation function applied to each Dense layer.
            self.has_bias: bool, A flag indicating whether a bias term is included (True or False).
            self.init_scale: float, A floatting number indicating the maximum value of initial random weights.
            self.dropout: float, A floatting number indicating the dropout rate in the network, can be [0, 1).
            self.backend: Literal["torch", "numpy"], The computational backend used by the layer.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self.n_encoder_modules: int, The number of layers that are encoder layers, used to perform forward_encoder().
            self._modules: Dict[nn_Module], The entire sequential archtecture stored in the module dictionary.
        """
        
        # Task check (Must in {"reg", "bin-cls", "mul-cls", "encoder-decoder"})
        task = task.lower()
        if task not in {"reg", "bin-cls", "mul-cls", "encoder-decoder"}:
            raise ValueError(f'Input `task` must in ("reg", "bin-cls", "mul-cls", "encoder-decoder"), but you have {task}')
        
        # Output dimension check
        if task == "bin-cls" and out_features > 1:
            raise ValueError(f"In `bin-cls` task, output must be a one column Tensor while values are in (0, 1) class scheme. But you have out_features = {out_features}")
        if task == "mul-cls" and out_features <= 1:
            raise ValueError(f"In `mul-cls` task, output must be a more-than-one column Tensor while values are in (0, 1) one-hot scheme. But you have out_features = {out_features}")
        
        # Dropout rate check (in [0,1))
        if dropout < 0 or dropout >= 1.0:
            raise ValueError(f"Argument `dropout` indicates dropout rate. Must be in [0, 1) but you have {dropout}")
        
        # Invoke the base constructor
        super().__init__(
            in_features = in_features, out_features = out_features, hidden = hidden,
            task = task, actv = actv, has_bias = has_bias, init_scale = init_scale, dropout = dropout,
            module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        
        # Iteratively build layers
        last = in_features
        
        # Build encoder hidden stacks (this determines backprop sequence)
        # 
        # Special note: here, hidden only represents for encoder network
        # and decoder will be constructed automatically and symmetrically
        for i, h in enumerate(hidden):
            
            # Dense Layer
            dense = Dense(last, h, 
                       has_bias=has_bias, init_scale=init_scale,
                       module_name=f"dense_{i}", 
                       backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
            self.__setattr__(f"dense_{i}", dense)
            
            # Activation Layer
            act = actv(
                       module_name=f"actv_{i}", 
                       backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
            self.__setattr__(f"actv_{i}", act)
            
            # Optional Dropout
            if i > 0 and h > in_features // 2 and h > 2 * out_features and i != (len(hidden) - 1) and dropout > 0:
                drop = Dropout(dropout, 
                       module_name=f"dropout_{i}", 
                       backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"dropout_{i}", drop)

            last = h
            
        # Build output head (after stacks)
        dense = Dense(last, out_features,
                     module_name="dense_head", 
                     backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
        self.__setattr__("dense_head", dense)
        if task == "reg":
            pass
        elif task == "bin-cls":
            head_act = Sigmoid(
                      module_name="actv_head", 
                      backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
            self.__setattr__("actv_head", head_act)
        elif task == "mul-cls":
            # Softmax will be applied by default in MultiCrossEntropy function, so only
            # outputs raw logits
            pass
        elif task == "encoder-decoder":
            pass
        
        # Record the number of modules in the _modules for the entire encoder arch
        self.__setattr__("n_encoder_modules", len(self._modules))
            
        # Build decoder pipelines if 'encoder-decoder' mode
        if task == "encoder-decoder":
            # In 'encoder-decoder' mode, no activation needed, only build heads
            dense = Dense(out_features, last, 
                         module_name="dense_decooder_head", 
                         backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
            self.__setattr__("dense_decooder_head", dense)
            
            # Build decoder hidden stacks if 'encoder-decoder' mode
            for i, h in enumerate(reversed(hidden)):
                # Inversed index calculated
                j = len(hidden) - i - 1
                
                # Next hidden dimension calculated
                if j > 0:
                    n = hidden[j - 1]   
                else:
                    n = in_features
                
                # Optional Dropout
                if j > 0 and h > in_features // 2 and h > 2 * out_features and j != (len(hidden) - 1) and dropout > 0:
                    drop = Dropout(dropout, 
                           module_name=f"dropout_decoder_{j}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                    self.__setattr__(f"dropout_decoder_{j}", drop)
                    
                # Activation Layer
                act = actv(
                           module_name=f"actv_decoder_{j}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"actv_decoder_{j}", act)
                    
                # Dense Layer
                dense = Dense(h, n,
                           has_bias=has_bias, init_scale=init_scale,
                           module_name=f"dense_decoder_{j}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"dense_decoder_{j}", dense)
                 
        return       

    def __repr__(self):
        return f"nn_auto_AutoMLP(MML Automatic MLP Modules \nArch:\n{self._modules})\n"
    
    
# Alias for nn_auto_AutoMLP
AutoMLP = nn_auto_AutoMLP


# Implementation of an Auto Time-Series Module
class nn_auto_AutoTMS(nn_auto_Sequential):
    """
    Auto-generated Time-Series (Recurrent-Dense-Dropout-Actv framework) ending with task-specific head.
    
    This is a automatic module that can generate a Recurrent-MLP module with inputs, outputs, hidden layers,
    capable of doing regression tasks (reg), binary and multiple classification tasks (bin-cls, mul-cls),
    auto-encoder based models are not currently supported (but may be supported in the future).
    It servces as a wrapped module providing a complete, auto-generated network structure
    where developpers can use it to create a simple and bench-mark level network in one line.
    """   
    
    __attr__ = "MML.nn_auto_AutoTMS"    
    
    def __init__(self, 
                 in_features: int, 
                 out_features: int, 
                 hidden: Sequence[int], 
                 task: Literal["reg", "bin-cls", "mul-cls"] = "reg", 
                 recurrent: type = LSTM,
                 recurrent_layers: int = 1,
                 actv: type = Tanh,
                 has_bias: bool = True,
                 init_scale: float = 0.1,
                 dropout: float = 0, 
                 *,
                 module_name: str = "nn_auto_AutoTMS",
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        Automatic Time Series Module Creator. It creates an automatic TMS module based on in, out, and hidden with recurrent blocks.
        Support tasks: 
            "reg": General regression task,
            "bin-cls": Binary Classification task,
            "mul-cls": Multiple Classification task,
            by defualt, it is set to "reg".
            Note: Auto-Encoders may be supported in the future, since it rarely used in this case.
        
        Parameters:
            in_features: int, The number of input features for this layer.
            out_features: int, The number of output features for this layer.
            hidden: Sequence of int, The dimension of hidden layers, can be a list of int or tuple of int.
                In this time-series case, hidden state's first element will be used as recurrent block's hidden size.
                So, if hidden is empty, it will raise an ValueError.
            task: str, The string name of the task name, can be {"reg", "bin-cls", "mul-cls"}, representing for:
                "reg": Regression, with linear output, may use MSE/RMSE/MAE as criterion,
                "bin-cls": Binary Classification, with Sigmoid activated output, may use BinaryCrossEntropy as criterion,
                "mul-cls": Multiple Classification, with raw logits output (Softmax will be applied in MultiCrossEntropy), may use MultiCrossEntropy as criterion,
                Auto-Encoder is currently NOT supported and may be supported in the future.
            recurrent: type, The class of Recurrent Module used in this stack, by default, we use `LSTM`.
                Note, this can be a custom module you implemented. As long as it follows the rule MML defines.
            recurrent_layers: int, The number of stacked recurrent layers. Defaults to 1.
            actv: type, The class of activation function applied to each Dense layer, by default, we use `Tanh`.
            has_bias: bool, A flag indicating whether to include a bias term. Valid values are True or False.
                    If set to True, the layer includes an additive bias term (b). Defaults to True.
            init_scale: float, The scale (maximum number) or weights that are randomly initialized. Defaults to 0.1.
            dropout: float, Dropout rate in some internal dropout layers (must be in [0, 1)). Defaults to 0.            
            module_name: str, The name of the module instance. Defaults to "nn_auto_AutoTMS".
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.in_features: int, The number of input features for this layer.
            self.out_features: int, The number of output features for this layer.
            self.hidden: Sequence of int, Dimensions of hidden layers (encoder only if any).
            self.task: float, The name of task stored, this impacts arch selection and output layer.
            self.recurrent: type, The class of recurrent stack used (like LSTM or RNN).
            self.recurrent_layers: int, The number of stacked recurrent layers.
            self.actv: type, The class of activation function applied to each Dense layer.
            self.has_bias: bool, A flag indicating whether a bias term is included (True or False).
            self.init_scale: float, A floatting number indicating the maximum value of initial random weights.
            self.dropout: float, A floatting number indicating the dropout rate in the network, can be [0, 1).
            self.backend: Literal["torch", "numpy"], The computational backend used by the layer.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self.n_encoder_modules: int, The number of layers that are encoder layers, used to perform forward_encoder().
            self._modules: Dict[nn_Module], The entire sequential archtecture stored in the module dictionary.
        """
        
        # Task check (Must in {"reg", "bin-cls", "mul-cls"})
        task = task.lower()
        if task not in {"reg", "bin-cls", "mul-cls"}:
            raise ValueError(f'Input `task` must in ("reg", "bin-cls", "mul-cls"), while "encoder-decoder" is currently not supported, but you have {task}')
        
        # Output dimension check
        if task == "bin-cls" and out_features > 1:
            raise ValueError(f"In `bin-cls` task, output must be a one column Tensor while values are in (0, 1) class scheme. But you have out_features = {out_features}")
        if task == "mul-cls" and out_features <= 1:
            raise ValueError(f"In `mul-cls` task, output must be a more-than-one column Tensor while values are in (0, 1) one-hot scheme. But you have out_features = {out_features}")
        
        # Dropout rate check (in [0,1))
        if dropout < 0 or dropout >= 1.0:
            raise ValueError(f"Argument `dropout` indicates dropout rate. Must be in [0, 1) but you have {dropout}")
        
        # Hidden must at least length 1
        if len(hidden) <= 0:
            raise ValueError(f"Argument `hidden` must be at least with 1 element. The 1st element will be used to indicate the hidden state dimension of the recurrent block, but you have {hidden}")
        
        # Invoke the base constructor
        super().__init__(
            in_features = in_features, out_features = out_features, hidden = hidden,
            task = task, actv = actv, has_bias = has_bias, init_scale = init_scale, dropout = dropout,
            module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd, **kwargs)
        
        # Record custom members
        self.__setattr__("recurrent", recurrent)
        self.__setattr__("recurrent_layers", recurrent_layers)
        
        # Iteratively build layers
        last = in_features
        
        # Build encoder hidden stacks (this determines backprop sequence)
        # 
        # Special note: here, hidden only represents for encoder network
        # and decoder will be constructed automatically and symmetrically
        # 
        # Special note: here, the first elem in hidden, hidden[0] represents
        # for the hidden dimension of the stacked recurrent blocks.
        for i, h in enumerate(hidden):
            
            # If the first one, recurrent layer
            if i == 0:
                
                # Recurrent Layer
                rec = recurrent(last, h, recurrent_layers,
                           has_bias=has_bias, init_scale=init_scale,
                           module_name=f"recurrent_{i}",
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"recurrent_{i}", rec)
            
            # Else, MLP layers
            else:
                
                # Dense Layer
                dense = Dense(last, h, 
                           has_bias=has_bias, init_scale=init_scale,
                           module_name=f"dense_{i}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"dense_{i}", dense)
                
                # Activation Layer
                act = actv(
                           module_name=f"actv_{i}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                self.__setattr__(f"actv_{i}", act)
                
                # Optional Dropout
                if i > 0 and h > in_features // 2 and h > 2 * out_features and i != (len(hidden) - 1) and dropout > 0:
                    drop = Dropout(dropout, 
                           module_name=f"dropout_{i}", 
                           backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
                    self.__setattr__(f"dropout_{i}", drop)

            last = h
            
        # Build output head (after stacks)
        dense = Dense(last, out_features,
                     module_name="dense_head", 
                     backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
        self.__setattr__("dense_head", dense)
        if task == "reg":
            pass
        elif task == "bin-cls":
            head_act = Sigmoid(
                      module_name="actv_head", 
                      backend=backend, dtype=dtype, device=device, autograd=autograd, **kwargs)
            self.__setattr__("actv_head", head_act)
        elif task == "mul-cls":
            # Softmax will be applied by default in MultiCrossEntropy function, so only
            # outputs raw logits
            pass

        # Record the number of modules in the _modules for the entire encoder arch
        self.__setattr__("n_encoder_modules", len(self._modules))
            
        # Encoder-Decoder NOT implemented, so return
        return
    
    def __repr__(self):
        return f"nn_auto_AutoTMS(MML Automatic Time-Series Modules \nArch:\n{self._modules})\n"
    
    
# Alias for nn_auto_AutoTMS
AutoTMS = nn_auto_AutoTMS


# Tests for nn_auto_AutoMLP
def test_auto_automlp():
    
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
    autoencoder = AutoMLP(X.shape[1], 8, [64, 32], task="encoder-decoder",
                      dropout=0.2,
                      backend="torch", device="cuda", dtype=torch.float32)
    
    # Then, we define a classifier
    classifier = AutoMLP(X.shape[1] * 2, 1, hidden = [32, 8], task="bin-cls",
                     dropout=0.2,
                     backend="torch", device="cuda", dtype=torch.float32)
    
    ######
    # Train the AutoEncoder on positive data
    crit = RMSE(backend="torch", device="cuda", dtype=torch.float32)
    optm = AdamW(autoencoder.parameters(), backend="torch", device="cuda", dtype=torch.float32)
    eval1 = Evaluator("Eval", "regression", autoencoder, crit, optm)
    eval1.fit(X_pos, X_pos, 10000,
              batch_size=None,
              verbosity=1,
              evalset={"Train": (X_pos, X_pos)},
              evalmetrics=["mse", "rmse"])
    
    # Conduct the forward for all data and get residuals
    eval1.eval()
    autoencoder.eval()
    X_res = autoencoder.forward(X)
    X_dif = X - X_res
    
    ######
    # Train the classifier 
    crit = BinaryCrossEntropy(backend="torch", device="cuda", dtype=torch.float32)
    optm = AdamW(classifier.parameters(), backend="torch", device="cuda", dtype=torch.float32)
    eval2 = Evaluator("Eval2", "classification", classifier, crit, optm)
    eval2.fit(X_dif.hstack(X), y, 10000, one_hot=False,
              batch_size=None,
              verbosity=1,
              evalset={"Train": (X_dif.hstack(X), y)},
              evalmetrics=["logloss", "accuracy"])
    
    # Predict results
    eval2.eval()
    classifier.eval()
    y_pred = eval2.predict(X_dif.hstack(X))
    

# Tests for nn_auto_AutoTMS
def test_auto_autotms():
    
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
    classifier = AutoTMS(X.shape[2], 1, hidden = [32, 16, 8], task="bin-cls",
                     recurrent=LSTM, recurrent_layers=1,
                     dropout=0.2,
                     backend="torch", device="cuda", dtype=torch.float32)
    
    ######
    # Train the classifier 
    crit = BinaryCrossEntropy(backend="torch", device="cuda", dtype=torch.float32)
    optm = AdamW(classifier.parameters(), backend="torch", device="cuda", dtype=torch.float32)
    eval2 = Evaluator("Eval2", "classification", classifier, crit, optm)
    eval2.fit(X, y, 10000, one_hot=False,
              batch_size=None,
              verbosity=1, evalper=1,
              evalset={"Train": (X, y)},
              evalmetrics=["logloss", "accuracy"])
    
    # Predict results
    eval2.eval()
    classifier.eval()
    y_pred = eval2.predict(X)
    