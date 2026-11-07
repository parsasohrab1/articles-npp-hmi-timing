"""Reproduce outputs/results.json from the public NPPAD runs.

    python scripts/run_experiment.py
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hmitime import conformal, data, features, openset

ROOT = os.path.join(os.path.dirname(__file__), "..")
runs_dir = os.path.join(ROOT, "data", "runs")
if not os.path.isdir(runs_dir) or not os.listdir(runs_dir):
    data.download(runs_dir)
X, y, _ids = data.load(runs_dir)
WINDOWS = [20, 40, 60, 90, 120, 180, 300, 600]
ALPHAS = (0.05, 0.10)
NSPLIT = 10
K = len(data.TYPES)
out = {
    "n_runs": len(y),
    "types": data.TYPES,
    "runs_per_type": {t: int((y == i).sum()) for i, t in enumerate(data.TYPES)},
    "windows_s": WINDOWS,
    "alphas": list(ALPHAS),
    "closed_set": {},
    "open_set": {},
}


def split(seed):
    rng = np.random.default_rng(seed)
    tr, ca, te = [], [], []
    for c in range(K):
        idx = rng.permutation(np.where(y == c)[0])
        a, b = int(0.5 * len(idx)), int(0.75 * len(idx))
        tr += list(idx[:a])
        ca += list(idx[a:b])
        te += list(idx[b:])
    return np.array(tr), np.array(ca), np.array(te)


def fit(features_train, labels, seed):
    # n_jobs=1 keeps the fit deterministic on Windows. n_jobs=-1 respawns this
    # script under the process starter and the run dies without a traceback.
    model = RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=1)
    return model.fit(features_train, labels)


def _mean_std(rows, key):
    vals = [r[key] for r in rows]
    return [float(np.mean(vals)), float(np.std(vals))]


for alpha in ALPHAS:
    res = {w: [] for w in WINDOWS}
    first = []
    for seed in range(NSPLIT):
        tr, ca, te = split(seed)
        single_at = np.full(len(te), np.inf)
        for w in WINDOWS:
            f_tr, scale = features.window_features(X[tr], w)
            f_ca, _ = features.window_features(X[ca], w, scale)
            f_te, _ = features.window_features(X[te], w, scale)
            model = fit(f_tr, y[tr], seed)
            q = conformal.threshold(model.predict_proba(f_ca), y[ca], alpha)
            prob = model.predict_proba(f_te)
            pred = conformal.sets(prob, q)
            size = pred.sum(1)
            covered = pred[np.arange(len(te)), y[te]]
            single = size == 1
            res[w].append(
                {
                    "accuracy": float(np.mean(model.classes_[prob.argmax(1)] == y[te])),
                    "coverage": float(covered.mean()),
                    "mean_size": float(size.mean()),
                    "singleton": float(single.mean()),
                    "singleton_correct": float(np.mean(single & covered)),
                    "empty": float((size == 0).mean()),
                }
            )
            resolved = (single_at == np.inf) & single & covered
            single_at = np.where(resolved, w, single_at)
        first.append(single_at)
    times = np.concatenate(first)
    resolved = np.isfinite(times)
    by_window = {}
    for w in WINDOWS:
        by_window[str(w)] = {k: _mean_std(res[w], k) for k in res[w][0]}
    timing = {
        "median_of_resolved": float(np.median(times[resolved])) if resolved.any() else None,
        "share_resolved_by_60s": float(np.mean(times <= 60)),
        "share_resolved_by_120s": float(np.mean(times <= 120)),
        "share_never_resolved_by_600s": float(np.mean(~resolved)),
    }
    out["closed_set"][f"alpha_{alpha}"] = {
        "by_window": by_window,
        "first_correct_singleton_s": timing,
    }
    print("alpha", alpha, timing, flush=True)

# Open set: one accident type is absent from training and calibration.
# Conformal NO_MATCH is the empty prediction set. Mahalanobis and energy
# are separate scores, calibrated so about alpha of known calibration runs
# sit above the threshold.
W = 300
SCORE_WINDOWS = (90, 120, 300)
rows = []
score_rows = {w: {kind: [] for kind in openset.KINDS} for w in SCORE_WINDOWS}
for c in range(K):
    rec = []
    score_rec = {w: {kind: [] for kind in openset.KINDS} for w in SCORE_WINDOWS}
    print("open set held-out", data.TYPES[c], flush=True)
    for seed in range(5):
        tr, ca, te = split(seed)
        tr_known, ca_known = tr[y[tr] != c], ca[y[ca] != c]
        unknown = np.concatenate([tr[y[tr] == c], ca[y[ca] == c], te[y[te] == c]])
        te_known = te[y[te] != c]
        f_tr, scale = features.window_features(X[tr_known], W)
        f_ca, _ = features.window_features(X[ca_known], W, scale)
        f_unknown, _ = features.window_features(X[unknown], W, scale)
        f_known, _ = features.window_features(X[te_known], W, scale)
        classes = sorted(set(y[tr_known]))
        remap = {k: i for i, k in enumerate(classes)}
        model = fit(f_tr, np.array([remap[k] for k in y[tr_known]]), seed)
        q = conformal.threshold(
            model.predict_proba(f_ca),
            np.array([remap[k] for k in y[ca_known]]),
            0.05,
        )
        set_u = conformal.sets(model.predict_proba(f_unknown), q)
        set_k = conformal.sets(model.predict_proba(f_known), q)
        rec.append(
            {
                "unknown_empty": float((set_u.sum(1) == 0).mean()),
                "unknown_singleton_wrong": float((set_u.sum(1) == 1).mean()),
                "known_empty": float((set_k.sum(1) == 0).mean()),
            }
        )
        for window in SCORE_WINDOWS:
            f_tr_w, scale_w = features.window_features(X[tr_known], window)
            f_ca_w, _ = features.window_features(X[ca_known], window, scale_w)
            f_u_w, _ = features.window_features(X[unknown], window, scale_w)
            f_k_w, _ = features.window_features(X[te_known], window, scale_w)
            queries = [f_u_w, f_k_w, f_ca_w]
            for kind in openset.KINDS:
                s_u, s_k, s_ca = openset.scores(f_tr_w, y[tr_known], queries, kind)
                thr = openset.upper_threshold(s_ca, 0.05)
                score_rec[window][kind].append(
                    {
                        "unknown_detect": float(np.mean(s_u > thr)),
                        "known_reject": float(np.mean(s_k > thr)),
                        "auroc": openset.auroc(s_u, s_k),
                    }
                )
    rows.append(
        {
            "held_out": data.TYPES[c],
            **{k: float(np.mean([r[k] for r in rec])) for k in rec[0]},
        }
    )
    for window in SCORE_WINDOWS:
        for kind in openset.KINDS:
            block = score_rec[window][kind]
            score_rows[window][kind].append(
                {
                    "held_out": data.TYPES[c],
                    **{k: float(np.mean([r[k] for r in block])) for k in block[0]},
                }
            )

out["open_set"] = {
    "window_s": W,
    "alpha": 0.05,
    "per_type": rows,
    "mean_unknown_empty": float(np.mean([r["unknown_empty"] for r in rows])),
    "mean_unknown_singleton_wrong": float(np.mean([r["unknown_singleton_wrong"] for r in rows])),
    "mean_known_empty": float(np.mean([r["known_empty"] for r in rows])),
}


def _pack(per_type):
    return {
        "per_type": per_type,
        "mean_unknown_detect": float(np.mean([r["unknown_detect"] for r in per_type])),
        "mean_known_reject": float(np.mean([r["known_reject"] for r in per_type])),
        "mean_auroc": float(np.mean([r["auroc"] for r in per_type])),
    }


out["open_set_scores"] = {
    "alpha": 0.05,
    "seeds": 5,
    "n_components": 10,
    "note": (
        "Minimum class-conditional Mahalanobis distance and logistic energy, "
        "both in a 10-component PCA subspace fit on known training runs only. "
        "A run is flagged when its score exceeds the known-calibration threshold."
    ),
    "by_window": {
        str(window): {kind: _pack(score_rows[window][kind]) for kind in openset.KINDS}
        for window in SCORE_WINDOWS
    },
}
print(
    "open set conformal",
    out["open_set"]["mean_unknown_empty"],
    out["open_set"]["mean_unknown_singleton_wrong"],
    flush=True,
)
for window, block in out["open_set_scores"]["by_window"].items():
    for kind, summary in block.items():
        print(
            "open set",
            window,
            kind,
            summary["mean_unknown_detect"],
            summary["mean_known_reject"],
            summary["mean_auroc"],
            flush=True,
        )
os.makedirs(os.path.join(ROOT, "outputs"), exist_ok=True)
destination = os.path.join(ROOT, "outputs", "results.json")
with open(destination, "w") as handle:
    json.dump(out, handle, indent=1)
