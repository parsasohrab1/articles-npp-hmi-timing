import numpy as np


def threshold(p_cal, y_cal, alpha):
    """Split-conformal threshold on the score 1 - P(true class)."""
    s = 1.0 - p_cal[np.arange(len(y_cal)), y_cal]
    n = len(s)
    k = min(int(np.ceil((n + 1) * (1 - alpha))), n)
    return np.sort(s)[k - 1]


def sets(p, q):
    return (1.0 - p) <= q
