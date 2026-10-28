import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from hmitime.display_policy import policy
from hmitime.conformal import threshold, sets


def test_modes():
    n = ["A", "B", "C"]
    assert policy([], n)["mode"] == "NO_MATCH"
    assert policy([1], n)["mode"] == "SINGLE"
    assert policy([0, 2], n)["mode"] == "CANDIDATES"


def test_coverage_on_exchangeable_data():
    rng = np.random.default_rng(0)
    def draw(n):
        y = rng.integers(0, 3, n); p = rng.dirichlet(np.ones(3), n); p[np.arange(n), y] += 1; return p / p.sum(1, keepdims=True), y
    pc, yc = draw(2000); pt, yt = draw(5000)
    q = threshold(pc, yc, 0.1)
    assert sets(pt, q)[np.arange(5000), yt].mean() >= 0.88
