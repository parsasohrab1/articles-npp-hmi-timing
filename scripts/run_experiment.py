"""Reproduces outputs/results.json from the NPPAD runs (python scripts/run_experiment.py; downloads data on first run)."""
import json, os, sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hmitime import data, features, conformal

ROOT = os.path.join(os.path.dirname(__file__), "..")
runs_dir = os.path.join(ROOT, "data", "runs")
if not os.path.isdir(runs_dir) or not os.listdir(runs_dir):
    data.download(runs_dir)
X, y, ids = data.load(runs_dir)
WINDOWS, ALPHAS, NSPLIT = [20, 40, 60, 90, 120, 180, 300, 600], (0.05, 0.10), 10
K = len(data.TYPES)
out = {"n_runs": int(len(y)), "types": data.TYPES, "runs_per_type": {t: int((y == i).sum()) for i, t in enumerate(data.TYPES)},
       "windows_s": WINDOWS, "alphas": list(ALPHAS), "closed_set": {}, "open_set": {}}


def split(seed):
    rng = np.random.default_rng(seed)
    tr, ca, te = [], [], []
    for c in range(K):
        idx = rng.permutation(np.where(y == c)[0])
        a, b = int(.5 * len(idx)), int(.75 * len(idx))
        tr += list(idx[:a]); ca += list(idx[a:b]); te += list(idx[b:])
    return np.array(tr), np.array(ca), np.array(te)


def fit(F, yy, seed):
    return RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=-1).fit(F, yy)


for a in ALPHAS:
    res = {w: [] for w in WINDOWS}
    first = []
    for s in range(NSPLIT):
        tr, ca, te = split(s)
        single_at = np.full(len(te), np.inf)
        for w in WINDOWS:
            Ftr, sc = features.window_features(X[tr], w)
            Fca, _ = features.window_features(X[ca], w, sc)
            Fte, _ = features.window_features(X[te], w, sc)
            m = fit(Ftr, y[tr], s)
            q = conformal.threshold(m.predict_proba(Fca), y[ca], a)
            P = m.predict_proba(Fte)
            S = conformal.sets(P, q)
            size = S.sum(1)
            cov = S[np.arange(len(te)), y[te]]
            single = size == 1
            res[w].append(dict(accuracy=float(np.mean(m.classes_[P.argmax(1)] == y[te])), coverage=float(cov.mean()), mean_size=float(size.mean()),
                               singleton=float(single.mean()), singleton_correct=float(np.mean(single & cov)), empty=float((size == 0).mean())))
            single_at = np.where((single_at == np.inf) & single & cov, w, single_at)
        first.append(single_at)
    fs = np.concatenate(first)
    ok = np.isfinite(fs)
    out["closed_set"][f"alpha_{a}"] = {
        "by_window": {str(w): {k: [float(np.mean([r[k] for r in res[w]])), float(np.std([r[k] for r in res[w]]))] for k in res[w][0]} for w in WINDOWS},
        "first_correct_singleton_s": {"median_of_resolved": float(np.median(fs[ok])) if ok.any() else None,
                                      "share_resolved_by_60s": float(np.mean(fs <= 60)), "share_resolved_by_120s": float(np.mean(fs <= 120)),
                                      "share_never_resolved_by_600s": float(np.mean(~ok))}}
    print("alpha", a, out["closed_set"][f"alpha_{a}"]["first_correct_singleton_s"], flush=True)

# open set: hold one accident type out of training and calibration; evaluate the 300 s window
W = 300
rows = []
for c in range(K):
    rec = []
    for s in range(5):
        tr, ca, te = split(s)
        trk, cak = tr[y[tr] != c], ca[y[ca] != c]
        unk = np.concatenate([tr[y[tr] == c], ca[y[ca] == c], te[y[te] == c]])
        tek = te[y[te] != c]
        Ftr, sc = features.window_features(X[trk], W)
        Fca, _ = features.window_features(X[cak], W, sc)
        Fu, _ = features.window_features(X[unk], W, sc)
        Fk, _ = features.window_features(X[tek], W, sc)
        classes = sorted(set(y[trk]))
        rm = {k: i for i, k in enumerate(classes)}
        m = fit(Ftr, np.array([rm[k] for k in y[trk]]), s)
        q = conformal.threshold(m.predict_proba(Fca), np.array([rm[k] for k in y[cak]]), 0.05)
        Su, Sk = conformal.sets(m.predict_proba(Fu), q), conformal.sets(m.predict_proba(Fk), q)
        rec.append(dict(unknown_empty=float((Su.sum(1) == 0).mean()), unknown_singleton_wrong=float((Su.sum(1) == 1).mean()), known_empty=float((Sk.sum(1) == 0).mean())))
    rows.append({"held_out": data.TYPES[c], **{k: float(np.mean([r[k] for r in rec])) for k in rec[0]}})
out["open_set"] = {"window_s": W, "alpha": 0.05, "per_type": rows,
                   "mean_unknown_empty": float(np.mean([r["unknown_empty"] for r in rows])),
                   "mean_unknown_singleton_wrong": float(np.mean([r["unknown_singleton_wrong"] for r in rows])),
                   "mean_known_empty": float(np.mean([r["known_empty"] for r in rows]))}
print("open set", out["open_set"]["mean_unknown_empty"], out["open_set"]["mean_unknown_singleton_wrong"], flush=True)
os.makedirs(os.path.join(ROOT, "outputs"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "outputs", "results.json"), "w"), indent=1)
