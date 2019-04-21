from IPython.lib.deepreload import reload as dreload
import os, numpy as np, math, json, bcolz, scipy, cv2
import pandas as pd, pickle, string, sys
import matplotlib
import contextlib
from abc import abstractmethod
from functools import partial
from isoweek import Week
from pandas_summary import DataFrameSummary
from sklearn import metrics, ensemble, preprocessing
from pathlib import Path
from distutils.version import LooseVersion

from matplotlib import pyplot as plt, rcParams, animation

matplotlib.rc('animation', html='html5')
np.set_printoptions(precision=5, linewidth=110, suppress=True)

from ipykernel.kernelapp import IPKernelApp
def in_notebook(): return IPKernelApp.initialized()

def in_ipynb():
    try:
        cls = get_ipython().__class__.__name__
        return cls == 'ZMQInteractiveShell'
    except NameError:
        return False

import tqdm as tq
from tqdm import tqdm_notebook, tnrange

def clear_tqdm():
    inst = getattr(tq.tqdm, '_instances', None)
    if not inst: return
    try:
        for i in range(len(inst)): inst.pop().close()
    except Exception:
        pass

if in_notebook():
    def tqdm(*args, **kwargs):
        clear_tqdm()
        return tq.tqdm(*args, file=sys.stdout, **kwargs)
    def trange(*args, **kwargs):
        clear_tqdm()
        return tq.trange(*args, file=sys.stdout, **kwargs)
else:
    from tqdm import tqdm, trange
    tnrange=trange
    tqdm_notebook=tqdm

