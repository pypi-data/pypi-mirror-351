import torch
from einops import rearrange
from torch import nn


def exists(val):
    return val is not None


class SinusoidalEmbeddings(nn.Module):
    """
    Sinusoidal embeddings.

    Args:
        dim (int): The dimension of the embeddings.
        scale_base (int): The scale base for the positional embeddings.
        use_xpos (bool): Whether to use xpos or not.

    Attributes:
        inv_freq (torch.Tensor): The inverse frequencies.
        scale (torch.Tensor): The scale.

    Example:
        >>> module = SinusoidalEmbeddings(10)
        >>> x = torch.randn(10, 10)
        >>> y = module(x)
        >>> y.shape
        torch.Size([10, 10, 10])

    """

    def __init__(self, dim, scale_base=None, use_xpos=False):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

        # xpos related

        self.use_xpos = use_xpos
        self.scale_base = scale_base

        assert not (
            use_xpos and not exists(scale_base)
        ), "scale base must be defined if using xpos"

        scale = (torch.arange(0, dim, 2) + 0.4 * dim) / (1.4 * dim)
        self.register_buffer("scale", scale, persistent=False)

    def forward(self, x):
        """forward"""
        seq_len, device = x.shape[-2], x.device

        t = torch.arange(seq_len, device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum("i , j -> i j", t, self.inv_freq)
        freqs = torch.cat((freqs, freqs), dim=-1)

        if not self.use_xpos:
            return freqs, torch.ones(1, device=device)

        power = (t - (seq_len // 2)) / self.scale_base
        scale = self.scale ** rearrange(power, "n -> n 1")
        scale = torch.cat((scale, scale), dim=-1)

        return freqs, scale


def rotate_half(x):
    """Rotate the tensor by half."""
    x = rearrange(x, "b ... (r d) -> b ... r d", r=2)
    x1, x2 = x.unbind(dim=-2)
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(q, k, freqs, scale=1):
    """
    Apply rotary positional embeddings to the query and key tensors.

    Args:
        q (torch.Tensor): The query tensor.
        k (torch.Tensor): The key tensor.
        freqs (torch.Tensor): The frequencies.
        scale (torch.Tensor): The scale.

    """
    q_len = q.shape[-2]
    q_freqs = freqs[..., -q_len:, :]

    inv_scale = scale**-1

    if scale.ndim == 2:
        scale = scale[-q_len:, :]

    q = (q * q_freqs.cos() * scale) + (rotate_half(q) * q_freqs.sin() * scale)
    k = (k * freqs.cos() * inv_scale) + (
        rotate_half(k) * freqs.sin() * inv_scale
    )
    return q, k
