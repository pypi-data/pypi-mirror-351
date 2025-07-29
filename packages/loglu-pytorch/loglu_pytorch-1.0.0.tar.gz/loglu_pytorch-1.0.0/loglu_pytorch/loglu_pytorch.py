import torch
import torch.nn as nn
from torch.autograd import Function

class LogLUFunction(Function):
    @staticmethod
    def forward(ctx, input):
        epsilon = 1e-7
        ctx.save_for_backward(input)
        # We clip input to avoid log(0) for x = 1
        input_clipped = torch.clamp(input, max=1.0 - 1e-7)
        output = torch.where(input > 0, input, -torch.log(1 - input_clipped) + epsilon)
        return output

    @staticmethod
    def backward(ctx, grad_output):
        (input,) = ctx.saved_tensors
        # Avoid division by zero
        input_clipped = torch.clamp(input, max=1.0 - 1e-7)
        grad_input = torch.where(input > 0, torch.ones_like(input), 1.0 / (1.0 - input_clipped))
        return grad_output * grad_input

class LogLU(nn.Module):
    def __init__(self):
        super(LogLU, self).__init__()

    def forward(self, input):
        return LogLUFunction.apply(input)
