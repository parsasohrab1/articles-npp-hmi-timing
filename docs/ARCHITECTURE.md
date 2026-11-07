# Architecture

```
NPPAD CSV runs ──► data.py (load, stack to runs x time x 97 vars)
                      │
                      ▼
              features.py (window ending t seconds after insertion)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  RandomForest (train runs)   conformal.py (calibration runs → threshold q)
        └─────────────┬─────────────┘
                      ▼
          prediction set per test run and window
                      │
                      ▼
            display_policy.py → SINGLE / CANDIDATES / NO_MATCH

              features of known training runs
                      │
                      ▼
              openset.py → Mahalanobis distance, logistic energy
                      │
                      ▼
        scripts/run_experiment.py → outputs/results.json
```

Design choices: run-level grouping avoids leakage between windows of the same run; one model per window length keeps the calibration valid for that window; the open-set test removes a class from both training and calibration so that the empty set is the only honest conformal answer. The Mahalanobis and energy scores are fit on the known training runs of that same split, and their thresholds are set on the known calibration runs. They are reported beside the conformal result; they do not change the display mode.
