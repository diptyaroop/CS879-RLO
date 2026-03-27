import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import hadamard

import ipywidgets as widgets
from IPython.display import display, clear_output


def rand_pm1(n):
    return np.where(np.random.rand(n) < 0.5, -1, 1)

def make_codes(U, L):
    H = hadamard(L)
    idx = np.random.choice(L, U, replace=False)
    return H[idx]

def cdma_once(U=3, L=16, noise=0, bits=None, codes=None):
    if codes is None:
        codes = make_codes(U, L)
    if bits is None:
        bits = rand_pm1(U)

    tx_users = codes * bits[:, None]     # (U,L)
    sum_sig = tx_users.sum(axis=0)       # (L,)
    rx = sum_sig + noise * np.random.randn(L)

    corrs = codes @ rx                   # (U,)
    rec_bits = np.where(corrs >= 0, 1, -1)
    return codes, bits, rx, corrs, rec_bits

