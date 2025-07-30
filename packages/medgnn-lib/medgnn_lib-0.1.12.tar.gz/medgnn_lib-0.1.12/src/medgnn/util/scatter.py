try:
  from torch_scatter import scatter_mean
  TORCH_SCATTER = True
except ImportError:
  TORCH_SCATTER = False

from typing_extensions import TYPE_CHECKING
if TYPE_CHECKING or not TORCH_SCATTER:
  import torch
  from torch import Tensor
  def scatter_mean(src: Tensor, index: Tensor, dim: int = -1, dim_size: int | None = None) -> Tensor:
    # Normalize negative dim
    dim = dim if dim >= 0 else src.dim() + dim

    # Expand index to match src shape
    if index.dim() != src.dim():
        # Insert singleton dimension at the correct axis
        for _ in range(src.dim() - index.dim()):
            index = index.unsqueeze(-1)
        index = index.expand_as(src)

    # Auto-infer dim_size if not given
    if dim_size is None:
        dim_size = int(index.max().item()) + 1

    # Set up output shape
    out_shape = list(src.shape)
    out_shape[dim] = dim_size

    out = torch.zeros(*out_shape, dtype=src.dtype, device=src.device)
    count = torch.zeros_like(out)

    out = torch.scatter_reduce(out, dim, index, src, reduce='sum', include_self=False)
    count = torch.scatter_reduce(count, dim, index, torch.ones_like(src), reduce='sum', include_self=False)

    return out / count.clamp(min=1)