from torch import nn, Tensor


class FractoralNorm(nn.Module):
    """
    FractoralNorm module applies LayerNorm to the input tensor multiple times in a row.

    Args:
        dim (int): Number of features in the input tensor.
        depth (int): Number of times to apply LayerNorm.
    """

    def __init__(self, dim: int, depth: int, *args, **kwargs):
        super().__init__()

        self.layers = nn.ModuleList(
            [nn.LayerNorm(dim, *args, **kwargs) for _ in range(depth)]
        )

    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass of the FractoralNorm module.

        Args:
            x (Tensor): Input tensor.

        Returns:
            Tensor: Output tensor after applying LayerNorm multiple times.
        """
        for layer in self.layers:
            x = layer(x)
        return x
