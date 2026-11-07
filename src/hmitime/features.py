"""Features at a window ending `seconds_after` seconds after accident insertion: change from t=0, last-30-s slope, running max change."""
import numpy as np

from .data import DT, INSERT_S


def window_features(X, seconds_after, scale=None):
    e = (INSERT_S + seconds_after) // DT
    d0 = X[:, e, :] - X[:, 0, :]
    slope = X[:, e, :] - X[:, e - 3, :]
    mx = np.abs(X[:, : e + 1, :] - X[:, :1, :]).max(1)
    F = np.concatenate([d0, slope, mx], 1)
    if scale is None:
        scale = F.std(0) + 1e-9
    return F / scale, scale
