import torch
from torch import Tensor, nn
import medgnn

class DownwardMP(nn.Module):
  def __init__(self, *, sample_dim: int, feature_dim: int, residual: bool = True):
    super().__init__()
    self.residual = residual
    self.proj = nn.Sequential(
      nn.Linear(sample_dim + feature_dim, feature_dim),
      nn.ReLU(),
      nn.Linear(feature_dim, feature_dim),
    )

  def forward(self, H: Tensor, S: Tensor) -> Tensor:
    """
    - H: [n, d, feature_dim] — current feature embeddings
    - S: [n, sample_dim]     — sample embeddings
    - Returns: updated feature embeddings [n, d, feature_dim]
    """
    n, d, _ = H.shape
    S_exp = S[:, None, :].expand(n, d, -1)         # [n, d, sample_dim]
    inputs = torch.cat([S_exp, H], dim=-1)         # [n, d, sample + feature]
    out = self.proj(inputs)                        # [n, d, feature_dim]
    return H + out if self.residual else out


class AcrossMP(nn.Module):
  def __init__(self, feature_dim: int, batch_size: int | None = 64):
    super().__init__()
    self.message_proj = nn.Linear(feature_dim, feature_dim)
    self.batch_size = batch_size

  def forward(self, H: torch.Tensor, knn_idx: torch.Tensor) -> torch.Tensor:
    """
    H: [n, d, h]
    knn_idx: [d, n, k]
    Returns: H_out: [n, d, h]
    """
    n, d, h = H.shape
    k = knn_idx.shape[-1]
    bs = self.batch_size
    H_out = H.clone()

    if bs is None or bs >= d:
      bs = d

    for start in range(0, d, bs):
      end = min(start + bs, d)
      b = end - start

      # Slice batch
      knn_batch = knn_idx[start:end]                          # [b, n, k]
      feature_ids = torch.arange(start, end, device=H.device).view(b, 1, 1).expand(b, n, k)
      target_ids = torch.arange(n, device=H.device).view(1, n, 1).expand(b, n, k)

      # Flatten
      source = knn_batch.reshape(-1)       # [b * n * k]
      feature = feature_ids.reshape(-1)
      target = target_ids.reshape(-1)

      # Gather messages
      H_src = H[source, feature]           # [b * n * k, h]
      msgs = self.message_proj(H_src)

      # Create composite index for scatter
      scatter_idx = target * d + feature   # [b * n * k]

      # Use torch_scatter instead of scatter_reduce
      agg = medgnn.scatter_mean(msgs, scatter_idx, dim=0, dim_size=n * d)  # [n * d, h]
      H_agg = agg.view(n, d, h)[:, start:end, :]                    # [n, b, h]
      H_out[:, start:end, :] += H_agg

    return H_out


class UpwardMP(nn.Module):
  def __init__(self, *, sample_dim: int, feature_dim: int, residual: bool = True):
    super().__init__()
    self.residual = residual
    self.proj = nn.Sequential(
      nn.Linear(sample_dim + feature_dim, sample_dim),
      nn.ReLU(),
      nn.Linear(sample_dim, sample_dim),
    )

  def forward(self, H: Tensor, S: Tensor) -> Tensor:
    """
    - `H :: [n, d, feature_dim]`: feature embeddings
    - `S :: [n, sample_dim]`: sample embeddings
    - Returns: updated sample embeddings `S' :: [n, sample_dim]`
    """
    n, d, _ = H.shape
    S_exp = S[:, None, :].expand(n, d, -1)  # [n, d, sample_dim]
    inputs = torch.cat([S_exp, H], dim=-1)  # [n, d, sample+feature]
    msgs = self.proj(inputs)                # [n, d, sample_dim]
    out = msgs.mean(dim=1)                  # [n, sample_dim]
    return S + out if self.residual else out


class LayerMP(nn.Module):
  def __init__(
      self, *, feature_dim: int, sample_dim: int,
      down_residual: bool = True, up_residual: bool = True,
      across_batch_size: int = 1024
    ):
    super().__init__()
    self.downward = DownwardMP(sample_dim=sample_dim, feature_dim=feature_dim, residual=down_residual)
    self.across = AcrossMP(feature_dim=feature_dim, batch_size=across_batch_size)
    self.upward = UpwardMP(sample_dim=sample_dim, feature_dim=feature_dim, residual=up_residual)

  def forward(self, H: Tensor, S: Tensor, knn_idx: Tensor) -> Tensor:
    H = self.downward(H, S)
    H = self.across(H, knn_idx)
    S = self.upward(H, S)
    return H, S


class BinaryModel(nn.Module):
  def __init__(
      self, *, feature_dim: int = 64, sample_dim: int = 64, num_layers: int = 3,
      across_batch_size: int | None = 1024, checkpoint: bool = False,
    ):
    super().__init__()
    self.checkpoint = checkpoint
    self.feature_proj = nn.Linear(1, feature_dim)
    self.sample_proj = nn.Linear(2, sample_dim)
    self.layers = nn.ModuleList([
      LayerMP(feature_dim=feature_dim, sample_dim=sample_dim, across_batch_size=across_batch_size)
      for _ in range(num_layers)
    ])
    self.classifier = nn.Linear(sample_dim, 1)

  def forward(self, H: torch.Tensor, S: torch.Tensor, knn_idx: Tensor) -> torch.Tensor:
    """- Feature values `H :: [n, d]`
    - Sample embeddings `S :: [n, num_classes]`
    - KNN indices `knn_idx :: [d, n, k]`
    - Returns `logits :: [n]`"""
    H = self.feature_proj(H[..., None])
    S = self.sample_proj(S)
    for layer in self.layers:
      if self.checkpoint:
        from torch.utils.checkpoint import checkpoint
        H, S = checkpoint(layer, H, S, knn_idx, use_reentrant=False)
      else:
        H, S = layer(H, S, knn_idx)
    return self.classifier(S)[..., 0]  # [n, 1] -> [n]
  
  def predict(self, X: torch.Tensor, knn_idx: Tensor) -> torch.Tensor:
    S = torch.zeros(X.shape[0], 2, device=X.device)
    return self(X, S, knn_idx)