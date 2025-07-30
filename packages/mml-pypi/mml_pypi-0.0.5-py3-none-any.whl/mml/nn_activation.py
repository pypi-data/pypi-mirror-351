# nn_activation.py
#
# Neural Network Activation Function Collection
# From MML Library by Nathmath

import numpy as np
try:
    import torch
except ImportError:
    torch = None

from typing import Any, Literal
    
from .objtyp import Object
from .tensor import Tensor

from .nn_parameter import nn_Parameter
from .nn_module import nn_Module


# Implementation of ReLU Activation
class nn_Activation_ReLU(nn_Module):
    """
    ReLU activation function.
    
    The Rectified Linear Unit (ReLU) is a widely used activation function 
    defined by the formula: f(x) = \max(0, x). This function outputs the 
    input value if it is positive, and zero otherwise. ReLU is celebrated for its 
    computational efficiency and ability to mitigate vanishing gradient problems 
    during backpropagation, making it a cornerstone in modern deep learning architectures.
    
    Formula: f(x) = max(0, x)
    
    """
    
    __attr__ = "MML.nn_Activation_ReLU"
    
    def __init__(self, 
                 *,
                 module_name: str = "nn_Activation_ReLU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        An ReLU activation function.

        Parameters:
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Rectified Linear Unit (ReLU) activation function to the input tensor.

        This method computes the element-wise ReLU activation, which outputs the input if it is positive,
        and zero otherwise. It is a fundamental non-linearity in neural networks, enabling the model
        to learn complex patterns by introducing non-linearities. The input is saved for backward propagation
        to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The ReLU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the ReLU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Apply ReLU to the input data
        return Tensor.where_as(x.data > 0, x.data, 0, backend=self.backend, dtype=self.dtype, device=self.device)

    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Pass gradient only where input was positive
        grad_input = Tensor.where_as(self.input.data <= 0, 0, grad_output.data, backend=self.backend, dtype=self.dtype, device=self.device)
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_ReLU(ReLU Activation Function)."
    

# Alias for nn_Activation_ReLU
ReLU = nn_Activation_ReLU


# Implementation of Leaky ReLU Activation
class nn_Activation_LeakyReLU(nn_Module):
    """
    Leaky ReLU activation with a small slope for negative inputs.
    
    The Leaky Rectified Linear Unit (Leaky ReLU) is a variant of the ReLU 
    activation function that allows a small, non-zero gradient when the input 
    is negative. This helps mitigate the "dying ReLU" problem where neurons 
    become inactive and cease to learn. The function is defined as:
    
    Formula: f(x) = max(0, x, α*x), where α is a small positive slope (typically 0.01).
    
    """
    
    __attr__ = "MML.nn_Activation_LeakyReLU"
    
    def __init__(self, 
                 leaky_slope: float = 0.01,
                 *,
                 module_name: str = "nn_Activation_ReLU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Leaky ReLU activation function.

        Parameters:
            leaky_slope: float, The slope of negative values.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.leaky_slope: float, The slope applied to negative values.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the leaky slope as a non-Parameter attribute
        self.__setattr__("leaky_slope", leaky_slope)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Leaky Rectified Linear Unit (Leaky ReLU) activation function to the input tensor.

        This method computes the element-wise Leaky ReLU activation, which outputs the input if it is positive,
        and a small negative slope multiplied by the input otherwise. This variant of ReLU mitigates the "dying ReLU"
        problem by allowing a controlled negative slope, improving gradient flow for negative inputs. The input is saved
        for backward propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The Leaky ReLU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the Leaky ReLU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Apply Leaky ReLU to the input data
        return Tensor.where_as(x.data > 0, x.data, x.data * self.leaky_slope, backend=self.backend, dtype=self.dtype, device=self.device)

    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Pass gradient only where input was positive
        grad_input = Tensor.where_as(self.input.data <= 0, grad_output.data * self.leaky_slope, grad_output.data, backend=self.backend, dtype=self.dtype, device=self.device)
        return grad_input
    
    def __repr__(self):
        return f"nn_Activation_LeakyReLU(Leaky ReLU Activation Function with alpha = {self.leaky_slope})."
    
      
# Alias for nn_Activation_LeakyReLU
LeakyReLU = nn_Activation_LeakyReLU 


# Implementation of GELU Activation
class nn_Activation_GELU(nn_Module):
    """
    GELU (Gaussian Error Linear Unit) activation, 
    a smooth, non-linear activation function commonly used in neural networks, especially in transformer architectures like BERT.
    
    The GELU activation is smooth and differentiable everywhere, unlike ReLU which has a kink at 0.
    The shape of GELU resembles a soft sigmoid-like activation near zero, but linear
    for large positive x and tapering off for large negative x.
    
    Formula:  By default the approximate formulation used in most deep‑learning libraries is applied:
        f(x) = 0.5 · x · (1 + tanh( √(2/π) · (x + 0.044715 · x^3) ) )

    Optionally, the exact formulation based on the Gaussian CDF can be selected:
        f(x) = 0.5 · x · (1 + erf( x / √2 ))
    """
    
    __attr__ = "MML.nn_Activation_GELU"
    
    def __init__(self, 
                 method: Literal["tanh", "erf"] | None = None,
                 *,
                 module_name: str = "nn_Activation_GELU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Softplus activation function.

        Parameters:
            method : Literal["tanh", "erf"] | None, Method to approximate GLU. Defaults to None, i.e., tanh.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.method: Literal["tanh", "erf"], Converted method to approximate GELU.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the converted method
        if method is None:
            method = "tanh"
        if method not in {"tanh", "erf"}:
            raise ValueError(f"The input `method` must be None or Literal['tanh', 'erf'], but you have {method}")
        self.__setattr__("method", method)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Gaussian Error Linear Unit (GELU) activation function to the input tensor.

        This method computes the element-wise GELU activation, which is smooth and differentiable everywhere, 
        unlike ReLU which has a kink at 0. The shape of GELU resembles a soft sigmoid-like 
        activation near zero, but linear for large positive x and tapering off for large negative x.

        Args:
            x (Tensor): Input tensor of any shape. The Leaky ReLU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the GELU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Apply GELU in tanh mode
        if self.method == "tanh":
            # f(x) = 0.5 · x · (1 + tanh( √(2/π) · (x + 0.044715 · x³) ) )
            coeff = 0.044715 # Emperical value
            root_2_over_pi = (2 / np.pi) ** 0.5
            u = root_2_over_pi * (x + coeff * (x ** 3))
            tanh_u = u.tanh()
            output = 0.5 * x * (1.0 + tanh_u)
            
            # Cache tanh_u for backward uses
            self.__setattr__("tanh_u", tanh_u)
            
        # Apply GELU in True erf mode
        else:
            # f(x) = 0.5 · x · (1 + erf( x / √2 ))
            root_1_over_2 = 0.7071067811865475  # 1/√2
            erf_x_sqrt2 = (x * root_1_over_2).erf()
            output = 0.5 * x * (1.0 + erf_x_sqrt2)
            
            # Cache erf_x_sqrt2 for backward uses
            self.__setattr__("erf_x_sqrt2", erf_x_sqrt2)
        
        return output
           
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Apply GELU backward() in tanh mode
        if self.method == "tanh":
            # Forward: tanh_u = tanh( √(2/π) · (x + 0.044715 · x^3) ) 
            #          f(x) = 0.5 · x · (1 + tanh_u)
            # Backward: sech2_u = (1 - tanh_u^2)
            #           u_prime = √(2/π) * (1 + 3 * 0.044715 * x^2)
            #           dL/dx = dL/dy * [1/2 * (1+tanh_u) + 1/2 * (x * sech2_u * u_prime)]
            coeff = 0.044715 # Emperical value    
            root_2_over_pi = (2 / np.pi) ** 0.5
            # sech²(u) = 1 − tanh²(u)
            sech2_u = 1.0 - self.tanh_u ** 2  
            u_prime = root_2_over_pi * (1.0 + 3.0 * coeff * (self.input ** 2))
            gelu_grad = 0.5 * (1.0 + self.tanh_u) + 0.5 * self.input * sech2_u * u_prime
            grad_input = grad_output * gelu_grad
            
        # Apply GELU backward() in True erf mode
        else:
            # derivative of exact GELU
            root_1_over_2pi = 0.3989422804014327  # 1/√(2π)
            erf_term = self.erf_x_sqrt2
            exp_term = (-0.5 * (self.input ** 2)).exp()
            gelu_grad = 0.5 * (1.0 + erf_term) + x * root_1_over_2pi * exp_term
            grad_input = grad_output * gelu_grad
            
        return grad_input

    def __repr__(self):
        return "nn_Activation_GELU(GELU Activation Function)."
    
    
# Alias for nn_Activation_GELU
GELU = nn_Activation_GELU


# Implementation of Softplus Activation
class nn_Activation_Softplus(nn_Module):
    """
    Softplus activation, which is a smooth approximation of ReLU.
    
    The softplus activation attempts to avoid dead neuron problems from another perspective.
    It involves a log smoothed ReLU making negative inputs yields little output, and always non-zero 
    gradients everywhere, helping optimization flow smoothly.
    
    Formula: (x) = (1 / beta) · log(1 + exp(beta · x))
    where beta > 0 is a temperature‑like sharpness parameter (beta -> inf, approaches ReLU, beta -> 0 flattens the curve).  
    """
    
    __attr__ = "MML.nn_Activation_Softplus"
    
    def __init__(self, 
                 beta: float = 1.0,
                 *,
                 module_name: str = "nn_Activation_Softplus", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Softplus activation function.

        Parameters:
            beta : float, Controls the sharpness of the Softplus curve. Defaults to 1.0.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.beta: float, The smooth factor controls the sharpness of the curve.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the beta as a non-Parameter attribute
        if beta <= 0:
            raise ValueError("Input argument `beta` must be strictly positive.")
        self.__setattr__("beta", beta)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Softplus activation function to the input tensor.

        This method computes the element-wise Softplus activation, which outputs a rather smooth ReLU like curve.
        This variant of this Softplus mitigates the "dying ReLU" problem by smoothen the curve.
        The input is saved for backward propagation to compute gradients during training.
        A numerically stable form is used: z = beta · x; softplus(z) = max(z, 0) + log1p(exp(−|z|))

        Args:
            x (Tensor): Input tensor of any shape. The Softplus operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the Softplus activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Calculate z score
        z = x * self.beta
        
        # Apply softplus(z) = max(z, 0) + log1p(exp(−|z|))
        # Note, max(‑) & abs(‑) are element‑wise Tensor ops; log1p = log(1+something)
        max_z = Tensor.where_as(z.data > 0, x.data, 0.0, backend=self.backend, dtype=self.dtype, device=self.device)
        log1p_z = ((-z.abs()).exp() + 1).log()
        softplus_z = max_z + log1p_z

        # Applt softplus(x) = softplus(z) / self.beta
        output = softplus_z / self.beta
        
        return output

    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Gradient computation formula:
        #  d f(x)/d x = 1 / (1 + exp(−β · x))
        # Manually computing, it is ∂L/∂x = ∂L/∂y ⊙ σ(βx)
        #  where σ(t) = 1 / (1 + exp(−t)).
        
        # Sigmoid beta * x
        sigmoid_bx = (self.input * self.beta).sigmoid()
        
        # Gradient is dL/dy * sigmoid_bx
        grad_input = grad_output * sigmoid_bx
        return grad_input
    
    def __repr__(self):
        return f"nn_Activation_Softplus(Softplus Activation Function with smoothing beta = {self.beta})."
    
    
# Alias for nn_Activation_Softplus
Softplus = nn_Activation_Softplus
    

# Implementation of ELU Activation
class nn_Activation_ELU(nn_Module):
    """
    ELU (Exponential Linear Unit) activation function.

    ELU is smooth everywhere (unlike ReLU) and keeps negative outputs bounded,
    which tends to yield faster, more stable convergence than ReLU in many
    settings.
    
    Formula: Defined by a discrete function:
        f(x) = { x                       ,  x > 0
               { α · (exp(x) − 1)        ,  x ≤ 0
    """
    
    __attr__ = "MML.nn_Activation_ELU"
    
    def __init__(self, 
                 alpha: float = 1.0,
                 *,
                 module_name: str = "nn_Activation_ELU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Exponential Linear Unit (ELU) activation function.

        Parameters:
            alpha: float, Controls the negative-region saturation value. Defaults to 1.0.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.alpha float, The negative saturation value.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the alpha as a non-Parameter attribute
        if alpha <= 0:
            raise ValueError("Input argument `alpha` must be strictly positive.")
        self.__setattr__("alpha", alpha)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Exponential Linear Unit (ELU) activation function to the input tensor.

        This method computes the element-wise ELU activation, which outputs a rather smooth ReLU like curve.
        This variant of this ELU mitigates the "dying ReLU" problem by keeping negative outputs bounded.
        The input is saved for backward propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The ELU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the ELU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Calculate two discrete parts
        # f(x) = x               (x>0)
        #      = α·(exp(x)−1)    (x≤0)
        neg = self.alpha * (x.exp() - 1.0)  # Negative part
        output = Tensor.where_as(x.data > 0, x.data, neg.data, backend=self.backend, dtype=self.dtype, device=self.device)
        
        return output

    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Gradient computation formula:
        # derivative: 1           (x>0)
        #             α·exp(x)    (x≤0)  ==  output + α
        grad_neg = grad_output * (self.alpha * self.input.exp())
        grad_input = Tensor.where_as(self.input.data > 0, grad_output.data, grad_neg.data, backend=self.backend, dtype=self.dtype, device=self.device)
        return grad_input
    
    def __repr__(self):
        return f"nn_Activation_ELU(ELU Activation Function with saturation alpha = {self.alpha})."
    
    
# Alias for nn_Activation_ELU
ELU = nn_Activation_ELU
    
    
# Implementation of SELU Activation
class nn_Activation_SELU(nn_Module):
    """
    SELU (Scaled Exponential Linear Unit) activation function.

    SELU is smooth everywhere (unlike ReLU) and keeps activations 
    zero-mean and unit-variance (under certain conditions) without explicit batch‑norm layers.
    It is self-normalized, suitable for nets without manuall normalization.
    
    Formula: Defined by a discrete function:
        f(x) = λ · { x                          , x > 0
                   { α · (exp(x) − 1)           , x ≤ 0 }
                   
    Recommended constants from Klambauer et al. (2017):
        α = 1.6732632423543772848170429916717
        λ = 1.0507009873554804934193349852946

    """
    
    __attr__ = "MML.nn_Activation_SELU"
    
    # default alpha and lambda from the original paper (2017)
    __ALPHA_DEFAULT__  = 1.6732632423543772
    __LAMBDA_DEFAULT__ = 1.0507009873554805
    
    def __init__(self, 
                 alpha: float | None = None,
                 lmbda: float | None = None,
                 *,
                 module_name: str = "nn_Activation_SELU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Scaled Exponential Linear Unit (SELU) activation function.

        Parameters:
            alpha: float | None, Controls the negative-region saturation value. 
                    If set to None, then will use the default value in Klambauer (2017). Defaults to None.
            lmbda: float | None, Controls the general scale rate for the entire span.
                    If set to None, then will use the default value in Klambauer (2017). Defaults to None.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.alpha: float, The negative saturation value.
            self.lmbda: float, The overall scale ratio.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the alpha and lmbda as a non-Parameter attribute
        if alpha is None:
            alpha = self.__ALPHA_DEFAULT__
        if alpha <= 0:
            raise ValueError("Input argument `alpha` must be strictly positive.")
        self.__setattr__("alpha", alpha)
        
        if lmbda is None:
            lmbda = self.__LAMBDA_DEFAULT__
        if lmbda <= 0:
            raise ValueError("Input argument `lmbda` must be strictly positive.")
        self.__setattr__("lmbda", lmbda)
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Scaled Exponential Linear Unit (SELU) activation function to the input tensor.

        This method computes the element-wise SELU activation, which outputs a rather smooth ReLU like curve.
        This variant of this SELU mitigates the "dying ReLU" problem by keeping negative outputs bounded,
        and conducts an auto scaling on top of the standard ELU module.
        The input is saved for backward propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The SELU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the SELU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Calculate two discrete parts
        # f(x) = lambda * x               (x>0)
        #      = lambda * α·(exp(x)−1)    (x≤0)
        pos = self.lmbda * x
        neg = self.lmbda * self.alpha * (x.exp() - 1.0)
        output = Tensor.where_as(x.data > 0, pos.data, neg.data, backend=self.backend, dtype=self.dtype, device=self.device)
        return output
    
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Gradient computation formula:
        # derivative: λ                             (x>0)
        #             λ·α·exp(x) = λ·(out/lam + α)  (x≤0)

        grad_pos = grad_output * self.lmbda
        grad_neg = grad_output * self.lmbda * self.alpha * (self.input.exp())
        grad_input = Tensor.where_as(self.input.data > 0, grad_pos.data, grad_neg.data, backend=self.backend, dtype=self.dtype, device=self.device)
        return grad_input
    
    def __repr__(self):
        return f"nn_Activation_SELU(SELU Activation Function with saturation alpha = {self.alpha}, lambda = {self.lmbda})."
         
    
# Alias for nn_Activation_SELU
SELU = nn_Activation_SELU


# Implementation of SiLU Activation
class nn_Activation_SiLU(nn_Module):
    """
    SiLU (Sigmoid Linear Unit) or called Swish activation function.

    SiLU is smooth everywhere and has been shown to outperform ReLU-like
    functions in many modern CNN/Transformer architectures.
    
    Formula:
        f(x) = x · σ(x)  where σ(x) = 1 / (1 + exp(−x)), which is .sigmoid() in Tensor library.

    Derivative:
        f'(x) = σ(x) + x · σ(x) · (1 − σ(x))
    """
    
    __attr__ = "MML.nn_Activation_SiLU"
    
    def __init__(self, 
                 *,
                 module_name: str = "nn_Activation_SiLU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Sigmoid Linear Unit (SiLU) activation function.

        Parameters:
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Sigmoid Linear Unit (SiLU) activation function to the input tensor.

        This method computes the element-wise SiLU activation, which outputs a rather smooth ReLU like curve.
        This variant of this SiLU mitigates the "dying ReLU" problem by introducing a sigmoid function and outperforms 
        than LeakyReLU with its smooth property.
        The input is saved for backward propagation to compute gradients during training.
        The sigmoided input is also saved for backward propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The SiLU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the SiLU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # f(x) = x · σ(x)  where σ(x) = 1 / (1 + exp(−x))
        sig_x = x.sigmoid()    # σ(x)
        output = x * sig_x     # x · σ(x)
        
        # Save the sigmoided input
        self.__setattr__("sig_x", sig_x)
        
        return output
    
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Gradient computation formula: f'(x) = σ(x) + x · σ(x) · (1 − σ(x))
        grad = self.sig_x + self.input * self.sig_x * (1.0 - self.sig_x)
        grad_input = grad_output * grad
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_SiLU(SiLU Activation Function)."
         
    
# Alias for nn_Activation_SiLU
SiLU = nn_Activation_SiLU
Swish = nn_Activation_SiLU
    

# Implementation of HardSiLU Activation
class nn_Activation_HardSiLU(nn_Module):
    """
    Hard-SiLU (Hard Sigmoid Linear Unit) or called Swish activation function.

    Hard-SiLU is a computationally efficient approximation of SiLU that retains 
    smoothness almost everywhere and has demonstrated strong empirical performance in 
    lightweight CNNs and mobile-friendly Transformer variants.
    
    Formula (ReLU6):
        f(x) = x · ReLU6(x + 3) / 6
             = ⎧ 0                       , x ≤ −3
               ⎨ x · (x + 3) / 6         , −3 < x < 3
               ⎩ x                       , x ≥ 3

    Derivative:
        f'(x) = ⎧ 0                      , x ≤ −3
                ⎨ x/3 + 0.5              , −3 < x < 3
                ⎩ 1                      , x ≥ 3
    """
    
    __attr__ = "MML.nn_Activation_HardSiLU"
    
    def __init__(self, 
                 *,
                 module_name: str = "nn_Activation_HardSiLU", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        A Hard Sigmoid Linear Unit (Hard-SiLU) activation function.

        Parameters:
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Hard Sigmoid Linear Unit (HardSiLU) activation function to the input tensor.

        This method computes the element-wise HardSiLU activation, which is a computationally efficient 
        approximation of SiLU that retains smoothness almost everywhere and has 
        demonstrated strong empirical performance in lightweight CNNs and mobile-friendly Transformer variants.
        The input is saved for backward propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The SiLU operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the SiLU activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Save input for backward
        self.__setattr__("input", x)

        # Forward formula
        # f(x) = x · ReLU6(x + 3) / 6
        #       = ⎧ 0                       , x ≤ −3
        #         ⎨ x · (x + 3) / 6         , −3 < x < 3
        #         ⎩ x                       , x ≥ 3
        
        # Middle segment: x * (x + 3) / 6
        mid = x * (x + 3.0) / 6.0

        # Piece‑wise stitching with Tensor.where_as
        output = Tensor.where_as(x.data >= 3.0, x.data, mid.data, backend=self.backend, dtype=self.dtype, device=self.device)
        output = Tensor.where_as(x.data <= -3.0, 0.0, output.data, backend=self.backend, dtype=self.dtype, device=self.device)
        
        return output
  
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Gradient computation formula:
        # f'(x) = ⎧ 0                     , x ≤ −3
        #         ⎨ x/3 + 0.5             , −3 < x < 3
        #         ⎩ 1                     , x ≥ 3
        grad_mid = (self.input / 3.0) + 0.5
        grad_piece = Tensor.where_as(self.input.data >= 3.0, 1.0, grad_mid.data, backend=self.backend, dtype=self.dtype, device=self.device)
        grad_piece = Tensor.where_as(self.input.data <= -3.0, 0.0, grad_piece.data, backend=self.backend, dtype=self.dtype, device=self.device)
        grad_input = grad_output * grad_piece
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_HardSiLU(HardSiLU Activation Function using ReLU6)."
         

# Alias for nn_Activation_HardSiLU
HardSiLU = nn_Activation_HardSiLU
HardSwish = nn_Activation_HardSiLU


# Implementation of Sigmoid Activation
class nn_Activation_Sigmoid(nn_Module):
    """
    Sigmoid activation function.
    
    The Sigmoid function maps input values to a range between 0 and 1, 
    making it suitable for binary classification tasks. It is defined by the 
    formula: f(x) = 1 / (1 + e^(-x)). However, it suffers from vanishing gradient 
    issues in deep networks due to its saturation regions near ±1.
    
    Formula: f(x) = \frac{1}{1 + e^{-x}}
    
    """
    
    __attr__ = "MML.nn_Activation_Sigmoid"
    
    def __init__(self, 
                 *,
                 module_name: str = "nn_Activation_Sigmoid", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        An Sigmoid activation function.

        Parameters:
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)

    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Sigmoid activation function to the input tensor.

        This method computes the element-wise Sigmoid activation, which maps input values
        to the range (0, 1). The Sigmoid function is widely used in neural networks for
        binary classification tasks due to its smooth, differentiable nature. The output
        is saved for use during backward propagation to compute gradients.

        Args:
            x (Tensor): Input tensor of any shape. The Sigmoid operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the Sigmoid activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.

        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Perform a sigmoid function on the input
        output = x.sigmoid()
        
        # Save output for backward
        self.__setattr__("output", output)

        return output
    
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # grad = grad_output * sigmoid(x) * (1 - sigmoid(x))
        grad_input = grad_output * self.output * (1 - self.output)
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_Sigmoid(Sigmoid Activation Function)."
    
    
# Alias for nn_Activation_Sigmoid
Sigmoid = nn_Activation_Sigmoid


# Implementation of Tanh Activation
class nn_Activation_Tanh(nn_Module):
    """
    Tanh activation function.
    
    The hyperbolic tangent (tanh) function maps input values to a range between -1 and 1,
    making it suitable for scenarios requiring symmetric output distribution. It is defined as:
    
    Formula: f(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}} = \tanh(x)
    
    """
    
    __attr__ = "MML.nn_Activation_Tanh"
    
    def __init__(self, 
                 *,
                 module_name: str = "nn_Activation_Sigmoid", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        An Sigmoid activation function.

        Parameters:
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Tangent Hyperbolic activation function to the input tensor.

        This method computes the element-wise hyperbolic tangent (tanh) activation,
        which maps input values to the range (-1, 1). The tanh function is smooth and
        differentiable everywhere, making it suitable for neural network layers that
        require non-linear transformations. The output is saved for use in backward
        propagation to compute gradients during training.

        Args:
            x (Tensor): Input tensor of any shape. The tanh operation is applied element-wise.

        Returns:
            Tensor: Output tensor after applying the tanh activation, with the same shape as the input.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.
        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Perform a tanh function on the input
        output = x.tanh()
        
        # Save output for backward
        self.__setattr__("output", output)

        return output
    
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # grad = grad_output * (1 - tanh(x)^2)
        grad_input = grad_output * (1 - self.output ** 2)
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_Tanh(Tanh Activation Function)."
   
    
# Alias for nn_Activation_Tanh
Tanh = nn_Activation_Tanh

   
# Implementation of Softmax Activation
class nn_Activation_Softmax(nn_Module):
    """
    Softmax activation function.
    
    The Softmax function converts raw scores (logits) into probabilities 
    that sum to 1, making it suitable for multi-class classification tasks. 
    It generalizes the sigmoid function to multiple classes by applying the 
    formula: f(x_i) = exp(x_i) / sum_j(exp(x_j)), where x_i is the input score 
    for class i. This ensures the output represents a probability distribution 
    over the classes.
    
    Formula: f(x_i) = \frac{e^{x_i}}{\sum_{j} e^{x_j}}
    
    """
    
    __attr__ = "MML.nn_Activation_Softmax"
    
    def __init__(self, 
                 dim: int = 1,
                 *,
                 module_name: str = "nn_Activation_Sigmoid", 
                 backend: Literal["torch", "numpy"] = "torch",
                 dtype: type | str = None,
                 device: str | None = None,
                 autograd: bool = False,
                 **kwargs):
        """
        An Sigmoid activation function.

        Parameters:
            dim: int, The dimension to apply softmax on. Defaults to 1.
            module_name: str, The name of the module instance.
            backend: Literal["torch", "numpy"], The computational backend to use. Defaults to "torch".
            dtype: type, The data type for the tensor values. Defaults to None (auto detection). 
                    For PyTorch, this corresponds to torch.dtype; for NumPy, it corresponds to np.dtype.
            device: str | None, The target device (e.g., "cpu", "cuda") where the layer's parameters will be placed. 
                    If None, uses the default device. Defaults to None (auto detection).
            autograd: bool, A flag indicating whether to use PyTorch's autograd for gradient computation. 
                    If True, manual gradient tracking is disabled. Defaults to False.

        Attributes:
            self.softmax_dim: int, The dimension to apply softmax on.
            self.dtype: type, The data type of the tensor values.
            self.device: str | None, The device where the parameters are placed.
            self.autograd: bool, Whether PyTorch's autograd is enabled for this layer.
            self._parameters.weight: nn_Parameter, The weight parameter matrix (shape: [in_features, out_features]).
            self._parameters.bias: nn_Parameter | optional, The optional bias vector (shape: [out_features]) if has_bias is True.
        """
        
        super().__init__(module_name = module_name, backend = backend, dtype = dtype, device = device, autograd = autograd)
    
        # Record the softmax dimension as a non-Parameter attribute
        self.__setattr__("softmax_dim", dim)
    
    def forward(self, x: Tensor) -> Tensor:
        """
        Apply the Softmax activation function to the input tensor.

        This method applies the softmax function along the specified axis (softmax_dim)
        to convert logits into probabilities. The output is a Tensor with the same shape
        as the input, but with values normalized to the range [0, 1] along the specified axis.
        This operation is commonly used in classification tasks to produce probability distributions.

        Args:
            x (Tensor): Input tensor containing logits (unnormalized log probabilities).
            softmax_dim (int): The axis along which to apply the softmax function. 
                              For example, for a batch of images, this could be the channel dimension.

        Returns:
            Tensor: Output tensor with probabilities computed via softmax along the specified axis.

        Raises:
            ValueError: If the input `x` is not a valid MML.Tensor object.

        """
                
        # Type check, x must be an instance of Tensor
        if isinstance(x, Tensor) == False:
            raise ValueError(f"In performing forward(), input `x` must be in a MML `Tensor` format but you have {type(x)}")
        
        # Perform a softmax function on the input
        output = x.softmax(axis = self.softmax_dim, keepdims = True)
        
        # Save output for backward
        self.__setattr__("output", output)

        return output
    
    def backward(self, grad_output: Tensor) -> Tensor:
        """
        Backward pass: compute gradients for weight, bias, and input.

        This method performs the gradient computation for a module during backpropagation. 
        It calculates the gradients of the loss with respect to the weights, biases, and input tensor,
        based on the provided `grad_output` (gradient from the next layer). The implementation
        supports both PyTorch autograd and manual gradient calculation modes.

        Args:
            grad_output (Tensor): Gradient tensor resulting from the output of the layer, used as input for backpropagation.

        Returns:
            Tensor: Gradient with respect to the input tensor, for recursive backward calculations in previous layers.

        Raises:
            ValueError: If `grad_output` is not a valid MML.Tensor object..
        """
        
        # If use autograd, pass; if manual mode, then calculate
        if self.autograd == True:
            return None
        
        # Type check, grad_output must be an instance of Tensor
        if isinstance(grad_output, Tensor) == False:
            raise ValueError(f"In performing backward(), `grad_output` must be in a MML `Tensor` format but you have {type(grad_output)}")
        
        # Compute gradient w.r.t input using Jacobian: grad_input = y * (grad_out - (grad_out * y).sum_along_dim)
        grad_sum = (grad_output * self.output).sum(axis=self.softmax_dim, keepdims=True) 
        grad_input = self.output * (grad_output - grad_sum)
        return grad_input
    
    def __repr__(self):
        return "nn_Activation_Softmax(Softmax Activation Function)."
   
    
# Alias for nn_Activation_Softmax
Softmax = nn_Activation_Softmax
 

# Test case of Activations
if __name__ == "__main__":
    
    from nn import Dense
    from nn import Softmax
    from nn import Module, nn_Module
    
    class any_test(Module):
        
        def __init__(self):
            
            super().__init__(module_name="any_test")
            self.dense = Dense(4, 2, True)
            self.softmax = Softmax()
            self.sumover = Dense(2, 1, False)
        
        def forward(self, inputs):
            out = self.dense.forward(inputs)
            out = self.softmax.forward(out)
            out = self.sumover.forward(out)
            return out
    
    inputs = Tensor([[1,2,3,4.],[2,3,4,5]], backend="torch")
    difference = Tensor([[0.002312],[0.002341]], backend="torch")    
    
    # Test forward
    x = any_test()
    x.train()
    x.forward(inputs)

    # Test backward
    x.backward(difference)
    