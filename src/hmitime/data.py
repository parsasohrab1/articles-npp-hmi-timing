"""Loader for the public NPPAD simulated PWR accident data set (Tsinghua / Micro-Simulation Technology, Sci. Data 2022).
Each run is a CSV with 97 plant variables sampled every 10 s; the accident is inserted at t = 20 s."""
import csv, glob, os, subprocess, urllib.request
import numpy as np

RAW = "https://raw.githubusercontent.com/thu-inet/NuclearPowerPlantAccidentData/master/Operation_csv_data/"
TYPES = ["FLB", "LLB", "LOCA", "LOCAC", "LR", "MD", "RI", "RW", "SGATR", "SGBTR", "SLBIC", "SLBOC"]
INSERT_S, DT = 20, 10
N_VARS = 97


def download(dest="data/runs", per_type=28):
    """Fetch the first per_type run files of each accident type (file names listed through the gh CLI)."""
    os.makedirs(dest, exist_ok=True)
    for t in TYPES:
        names = subprocess.run(["gh", "api", f"repos/thu-inet/NuclearPowerPlantAccidentData/contents/Operation_csv_data/{t}",
                                "--jq", ".[]|select(.size>1000)|.name"], capture_output=True, text=True, check=True).stdout.split()[:per_type]
        for n in names:
            p = os.path.join(dest, f"{t}_{n}")
            if not os.path.exists(p):
                urllib.request.urlretrieve(RAW + f"{t}/{n}", p)


def load(dest="data/runs", max_rows=70):
    X, y, ids = [], [], []
    for p in sorted(glob.glob(os.path.join(dest, "*.csv"))):
        t = os.path.basename(p).split("_")[0]
        if t not in TYPES:
            continue
        raw = list(csv.reader(open(p)))
        if len(raw[0]) != N_VARS or len(raw) < max_rows + 1:
            continue  # files with extra columns or too short to cover the longest window are skipped
        rows = raw[1:max_rows + 1]
        X.append(np.array([[float(v) for v in r[1:]] for r in rows]))
        y.append(TYPES.index(t))
        ids.append(os.path.basename(p))
    n = min(len(a) for a in X)
    return np.stack([a[:n] for a in X]), np.array(y), ids
