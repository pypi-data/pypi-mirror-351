import numpy as np

class k_fold:
  @staticmethod
  def split(X: np.ndarray, y: np.ndarray, *, k=5, perm: np.ndarray | None = None, ret_indices=False):
    """K-fold cross-validation generator. Yields `(X_train, y_train, X_val, y_val)` for each of the `k` folds."""
    n = X.shape[0]
    if perm is None:
      perm = np.random.permutation(n)
    n_test = n // k
    for i in range(k):
      val_idx = perm[n_test*i:n_test*(i+1)]
      train_idx = np.setdiff1d(perm, val_idx)
      if ret_indices:
        yield train_idx, val_idx
      else:
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        yield X_train, y_train, X_val, y_val

  @staticmethod
  def replicate(X: np.ndarray, y: np.ndarray, i: int, *, k=5, seed: int, ret_indices=False):
    """i-th fold of k-fold cross-validation. Returns `(X_train, y_train, X_val, y_val)`."""
    perm = np.random.default_rng(seed).permutation(X.shape[0])
    return k_fold.ith(X, y, i, k=k, perm=perm, ret_indices=ret_indices)

  @staticmethod
  def ith(X: np.ndarray, y: np.ndarray, i: int, *, k=5, perm: np.ndarray | None = None, ret_indices=False):
    """i-th fold of k-fold cross-validation. Returns `(X_train, y_train, X_val, y_val)`."""
    n = X.shape[0]
    if perm is None:
      perm = np.random.permutation(n)
    n_test = n // k
    val_idx = perm[n_test*i:n_test*(i+1)]
    train_idx = np.setdiff1d(perm, val_idx)
    if ret_indices:
      return train_idx, val_idx
    else:
      X_train, y_train = X[train_idx], y[train_idx]
      X_val, y_val = X[val_idx], y[val_idx]
      return X_train, y_train, X_val, y_val
    
  class stratified:
    @staticmethod
    def split(X: np.ndarray, y: np.ndarray, *, k=5, seed: int | None = None, ret_indices=False):
      from sklearn.model_selection import StratifiedKFold
      for train_idx, test_idx in StratifiedKFold(n_splits=k, shuffle=True, random_state=seed).split(X, y):
        if ret_indices:
          yield train_idx, test_idx
        else:
          X_train, y_train = X[train_idx], y[train_idx]
          X_val, y_val = X[test_idx], y[test_idx]
          yield X_train, y_train, X_val, y_val

    @staticmethod
    def ith(X: np.ndarray, y: np.ndarray, i: int, *, k=5, seed: int | None = None, ret_indices=False):
      all = k_fold.stratified.split(X, y, k=k, seed=seed, ret_indices=ret_indices)
      for j, fold in enumerate(all):
        if j == i:
          return fold
      raise ValueError(f"Fold {i} does not exist in {k}-fold cross-validation.")
    