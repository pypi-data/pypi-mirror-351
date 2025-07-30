import math

import torch
import torch.nn.functional as F
from torch import nn


def absmax_quantize(x, bits=8):
    """
    Absmax Quantization

    Args:
        x (torch.Tensor): Input tensor
        bits (int, optional): Number of bits. Defaults to 8.



    """
    Qb = 2 ** (bits - 1) - 1
    scale = Qb / torch.max(torch.abs(x))
    quant = (scale * x).round()
    dequant = quant / scale
    return quant.to(torch.int8), dequant


class BitLinear(nn.Module):
    """

    BitLinear

    Args:
        in_features (int): Size of each input sample
        out_features (int): Size of each output sample
        groups (int, optional): Number of groups. Defaults to 1.

    Usage:
        >>> import torch
        >>> from zeta.nn.quant.bitlinear import BitLinear
        >>> linear = BitLinear(10, 20)
        >>> input = torch.randn(128, 10)
        >>> output = linear(input)
        >>> print(output.size())
        torch.Size([128, 20])

    """

    def __init__(self, in_features, out_features, groups=1):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.groups = groups
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        self.reset_parameters()

    def reset_parameters(self):
        """Reset Parameters"""
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

    def forward(self, input):
        """Forward Pass"""
        # Group Quantization and Normalization
        weight = self.weight.view(self.groups, -1)

        weight = weight - weight.mean(dim=1, keepdim=True)
        weight = torch.sign(weight)

        beta = torch.abs(weight).sum(dim=1, keepdim=True) / (
            weight.shape[0] * weight.shape[1]
        )

        weight = weight * beta
        weight = weight.view(self.out_features, self.in_features)

        # Absmax Quantization
        quant_input, _ = absmax_quantize(input)

        # Linear
        output = F.linear(quant_input.float(), weight)

        # Dequantization
        output = output / beta.view(-1, 1)
        return output
