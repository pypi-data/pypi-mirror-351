from typing_extensions import Literal
import os
import numpy as np

DATA_PATH = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, 'data'))

def StandardScaler():
  from sklearn.preprocessing import StandardScaler
  return StandardScaler()

class load:
  @staticmethod
  def mat(name: str, data_path: str = DATA_PATH) -> tuple[np.ndarray, np.ndarray]:
    """Returns `(X, y)`, with `X :: [n, d]`, `y :: [n]`"""
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X = data['X']
    y = data.get('Y')
    if y is None:
      y = data['y']
    y = y[:, 0]
    return X, y

  @staticmethod
  def allaml(name: str = 'feature/ALLAML.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y
  
  @staticmethod
  def tox(name: str = 'feature/TOX_171.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y
  
  @staticmethod
  def cll(name: str = 'feature/CLL_SUB_111.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def gli(name: str = 'feature/GLI_85.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def prostate(name: str = 'feature/Prostate_GE.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def smk(name: str = 'feature/SMK_CAN_187.mat', data_path: str = DATA_PATH):
    X_raw, y_raw = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    y = y_raw-1 # {1, 2} -> {0, 1}
    return X, y

  @staticmethod
  def tran(name: str = 'tran.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def oscc(name: str = 'oscc-ms.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X_raw[np.isnan(X_raw)] = -1
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def lipid_nafld(name: str = 'lipid-nafld.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def tran_palm_10dRC(
    name: str = 'palm-10dRC/tran-palm-10dRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['sex', 'diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)
    
    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def prot_palm_10dRC(
    name: str = 'palm-10dRC/prot-palm-10dRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)
    
    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]
      
    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def meta_palm_10dRC(
    name: str = 'palm-10dRC/meta-palm-10dRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet', 'sex'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def serum_meta_palm_10dRC(
    name: str = 'palm-10dRC/serum-meta-palm-10dRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet', 'sex'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def lipid_palm_10dRC(
    name: str = 'palm-10dRC/lipid-palm-10dRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('diet',):
      data[key] = data[key][:, 0]

    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
    
  @staticmethod
  def palm_10dRC_datasets(
    data_path: str = DATA_PATH, *,
    labels: Literal['diet'] = 'diet', load_all: bool = False
  ):
    return {
      'tran-palm-10dRC': lambda: load.tran_palm_10dRC(data_path=data_path, labels=labels, load_all=load_all),
      'prot-palm-10dRC': lambda: load.prot_palm_10dRC(data_path=data_path, labels=labels, load_all=load_all),
      'meta-palm-10dRC': lambda: load.meta_palm_10dRC(data_path=data_path, labels=labels, load_all=load_all),
      'serum-meta-palm-10dRC': lambda: load.serum_meta_palm_10dRC(data_path=data_path, labels=labels, load_all=load_all),
      'lipid-palm-10dRC': lambda: load.lipid_palm_10dRC(data_path=data_path, labels=labels, load_all=load_all),
    }
  
  @staticmethod
  def tran_palm_nRC(
    name: str = 'palm-nRC/tran-palm-nRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['sex', 'diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)
    
    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def prot_palm_nRC(
    name: str = 'palm-nRC/prot-palm-nRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)
    
    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]
      
    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def meta_palm_nRC(
    name: str = 'palm-nRC/meta-palm-nRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet', 'sex'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def serum_meta_palm_nRC(
    name: str = 'palm-nRC/serum-meta-palm-nRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet', 'sex'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('sex', 'diet'):
      data[key] = data[key][:, 0]
    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
  
  @staticmethod
  def lipid_palm_nRC(
    name: str = 'palm-nRC/lipid-palm-nRC.mat', *, data_path: str = DATA_PATH,
    labels: Literal['diet'] = 'diet', load_all: bool = False
  ):
    from scipy.io import loadmat
    data: dict = loadmat(os.path.join(data_path, name))
    X_raw = data['X']
    del data['X']
    X = StandardScaler().fit_transform(X_raw)

    for key in ('diet',):
      data[key] = data[key][:, 0]

    y = data[labels]

    if load_all:
      data['ids'] = [id.strip() for id in data['ids']]
      return X, y, data
    else:
      return X, y
    

  @staticmethod
  def palm_nRC_datasets(
    data_path: str = DATA_PATH, *,
    labels: str = 'diet', load_all: bool = False
  ):
    return {
      'tran-palm-nRC': lambda: load.tran_palm_nRC(data_path=data_path, labels=labels, load_all=load_all),
      'prot-palm-nRC': lambda: load.prot_palm_nRC(data_path=data_path, labels=labels, load_all=load_all),
      'meta-palm-nRC': lambda: load.meta_palm_nRC(data_path=data_path, labels=labels, load_all=load_all),
      'serum-meta-palm-nRC': lambda: load.serum_meta_palm_nRC(data_path=data_path, labels=labels, load_all=load_all),
      'lipid-palm-nRC': lambda: load.lipid_palm_nRC(data_path=data_path, labels=labels, load_all=load_all),
    }
  
  @staticmethod
  def pancan(name: str = 'pancan.mat', data_path: str = DATA_PATH):
    X_raw, y = load.mat(name, data_path)
    X = StandardScaler().fit_transform(X_raw)
    return X, y
  
  @staticmethod
  def binary_datasets(data_path: str = DATA_PATH):
    return {
      'allaml': lambda: load.allaml(data_path=data_path),
      'gli': lambda: load.gli(data_path=data_path),
      'prostate': lambda: load.prostate(data_path=data_path),
      'smk': lambda: load.smk(data_path=data_path),
      'tran': lambda: load.tran(data_path=data_path),
      'oscc': lambda: load.oscc(data_path=data_path),
      'lipid-nafld': lambda: load.lipid_nafld(data_path=data_path),
    }

  @staticmethod
  def datasets(data_path: str = DATA_PATH):
    return load.binary_datasets(data_path) | {
      'tox': lambda: load.tox(data_path=data_path),
      'cll': lambda: load.cll(data_path=data_path),
    }