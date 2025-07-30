import torch

def topk_indices(X: torch.Tensor, k: int = 5) -> torch.Tensor:
  """
  Build top-k indices by similarity for each feature.

  Args:
      X: [n, d] — input matrix
      k: number of neighbors (excluding self)

  Returns:
      knn_idx: [d, n, k] — for each feature j, each sample i, k neighbor indices i'
  """
  n, d = X.shape
  X_T = X.T  # [d, n]
  knn_idx = torch.zeros(d, n, k, dtype=torch.long, device=X.device)

  for j in range(d):
    xj = X_T[j].unsqueeze(1)  # [n, 1]
    dist = torch.cdist(xj, xj, p=2)  # [n, n]
    topk = dist.topk(k + 1, largest=False).indices[:, 1:]  # [n, k], skip self
    knn_idx[j] = topk

  return knn_idx