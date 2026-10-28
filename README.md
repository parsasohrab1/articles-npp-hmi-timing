# HMI-Timing (articles-npp-hmi-timing)

How soon after a nuclear-plant accident begins can a data-driven aid show an operator a *certified* diagnosis, and what should the display show before that, or when the accident is unknown?

Method: run-level splits of the public NPPAD simulator data, random forest per time window, split-conformal prediction sets (95 % / 90 %), display states SINGLE / CANDIDATES / NO_MATCH, first-correct-singleton time, and a leave-one-accident-type-out open-set test.

## Run
```
pip install -r requirements.txt
python -m pytest -q tests
python scripts/run_experiment.py     # downloads data/runs on first use (needs the gh CLI), writes outputs/results.json
```

## Measured results (alpha = 0.05, 10 random run-level splits, 315 runs, 12 types)
| window after insertion | accuracy | coverage | single type shown | single and correct |
|---|---|---|---|---|
| 20-60 s | 0.26 | 0.95-0.96 | 0.09 | 0.09 |
| 90 s | 0.96 | 0.96 | 0.95 | 0.94 |
| 120 s | 0.95 | 0.96 | 0.93 | 0.91 |
| 300 s | 0.93 | 0.96 | 0.84 | 0.82 |
| 600 s | 0.90 | 0.96 | 0.84 | 0.81 |

- A correct single diagnosis was shown by 120 s in 95 % of test runs; 3.5 % were never resolved within 600 s.
- Open set (window 300 s): with one accident type withheld, only 2.9 % of its runs gave an empty set (NO_MATCH) and 69 % received a single wrong type. The NO_MATCH state is therefore **not** a reliable safeguard in this setup.

Full numbers: `outputs/results.json`.

## Limits
Simulator data from one PWR model, not plant data; 12 of the 18 published accident types are available as CSV; the SLBIC type has only 9 usable runs (files with extra columns or too few rows are skipped); no operator study; not a safety-classified function.

Data: NPPAD (Tsinghua / thu-inet), downloaded at run time, not stored here.
