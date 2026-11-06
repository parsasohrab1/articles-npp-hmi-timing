import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hmitime.openset import auroc, scores, upper_threshold


def test_threshold_flags_about_alpha():
    scores_cal = np.random.default_rng(1).random(2000)
    thr = upper_threshold(scores_cal, 0.1)
    rate = float(np.mean(scores_cal > thr))
    assert 0.07 < rate < 0.13


def _clouds(rng):
    known_a = rng.normal(0.0, 0.3, size=(40, 6))
    known_b = rng.normal(0.0, 0.3, size=(40, 6))
    known_b[:, 0] += 5.0
    train = np.vstack([known_a[:30], known_b[:30]])
    labels = np.array([0] * 30 + [1] * 30)
    calibration = np.vstack([known_a[30:], known_b[30:]])
    known_test = np.vstack(
        [rng.normal(0.0, 0.3, size=(20, 6)), rng.normal(0.0, 0.3, size=(20, 6))]
    )
    known_test[20:, 0] += 5.0
    return train, labels, calibration, known_test


def test_mahalanobis_flags_a_far_cluster():
    rng = np.random.default_rng(0)
    train, labels, calibration, known_test = _clouds(rng)
    unknown = rng.normal(0.0, 0.3, size=(30, 6))
    unknown[:, 1] += 12.0
    unknown_s, known_s, cal_s = scores(train, labels, [unknown, known_test, calibration], "mahalanobis")
    assert auroc(unknown_s, known_s) > 0.95
    thr = upper_threshold(cal_s, 0.1)
    assert float(np.mean(unknown_s > thr)) > 0.9
    assert float(np.mean(known_s > thr)) < 0.3


def test_energy_flags_low_confidence_points():
    """Logistic energy rises where the model is unsure, not merely where a point is far."""
    rng = np.random.default_rng(0)
    train, labels, calibration, known_test = _clouds(rng)
    midpoint = rng.normal(0.0, 0.3, size=(30, 6))
    midpoint[:, 0] += 2.5
    unknown_s, known_s, cal_s = scores(train, labels, [midpoint, known_test, calibration], "energy")
    assert auroc(unknown_s, known_s) > 0.95
    thr = upper_threshold(cal_s, 0.1)
    assert float(np.mean(unknown_s > thr)) > 0.9
    assert float(np.mean(known_s > thr)) < 0.3
