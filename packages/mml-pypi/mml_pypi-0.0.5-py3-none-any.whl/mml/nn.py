# nn.py
#
# A High-level Collection of Neural Network Components as Unified APIs
# From MML Library by Nathmath


# Tensor
from .tensor import Tensor

# Modules
from .nn_module import Module, nn_Module

# Layers
from .nn_layers import Dense, nn_Layer_Dense
from .nn_layers import Dropout, nn_Layer_Dropout
from .nn_layers import Flatten, nn_Layer_Flatten
from .nn_layers import RNN, StackedRNN, nn_Layer_StackedRNN
from .nn_layers import LSTM, StackedLSTM, nn_Layer_StackedLSTM

# Activations
from .nn_activation import ReLU, nn_Activation_ReLU
from .nn_activation import LeakyReLU, nn_Activation_LeakyReLU
from .nn_activation import GELU, nn_Activation_GELU
from .nn_activation import Softplus, nn_Activation_Softplus
from .nn_activation import ELU, nn_Activation_ELU
from .nn_activation import SELU, nn_Activation_SELU
from .nn_activation import SiLU, Swish, nn_Activation_SiLU
from .nn_activation import HardSiLU, HardSwish, nn_Activation_HardSiLU
from .nn_activation import Sigmoid, nn_Activation_Sigmoid
from .nn_activation import Tanh, nn_Activation_Tanh
from .nn_activation import Softmax, nn_Activation_Softmax

# Auto Frame
from .nn_auto_nn_frame import nn_auto_Sequential
from .nn_auto_nn_frame import AutoMLP, nn_auto_AutoMLP
from .nn_auto_nn_frame import AutoTMS, nn_auto_AutoTMS

# Losses
from .nn_loss import MSE, nn_Loss_MSE
from .nn_loss import RMSE, nn_Loss_RMSE
from .nn_loss import MAE, nn_Loss_MAE
from .nn_loss import BCE, BinaryCrossEntropy, nn_Loss_BinaryCrossEntropy
from .nn_loss import MCE, MultiCrossEntropy, nn_Loss_MultiCrossEntropy

# Optimizers
from .nn_optimizer import SGD, nn_Optm_SGD
from .nn_optimizer import Adam, nn_Optm_Adam
from .nn_optimizer import AdamW, nn_Optm_AdamW

# Auto Frameworks
from .nn_auto_nn_frame import nn_auto_Sequential
from .nn_auto_nn_frame import AutoMLP, nn_auto_AutoMLP
from .nn_auto_nn_frame import AutoTMS, nn_auto_AutoTMS

# SInterf Evaluator
from .nn_sinterf_evaluator import Evaluator, nn_SInterf_Evaluator

# SInterf AutoNeuralNet
from .nn_sinterf_autoneuralnet import AutoNN, AutoNeuralNet, nn_SInterf_AutoNeuralNetwork
