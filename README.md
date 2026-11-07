# HMI-Timing (articles-npp-hmi-timing)

How soon after a nuclear-plant accident begins can a data-driven aid show an operator a *certified* diagnosis, and what should the display show before that, or when the accident is unknown?

Method: run-level splits of the public NPPAD simulator data, random forest per time window, split-conformal prediction sets (95 % / 90 %), display states SINGLE / CANDIDATES / NO_MATCH, and first-correct-singleton time. The open-set test holds out one accident type. Besides the empty conformal set, it scores the same runs with a class-conditional Mahalanobis distance and with the energy of a multinomial logistic model (both in a 10-component PCA subspace fit only on the known training runs). Those scores do not change the display.

**Maturity: TRL 4 for closed-set timing on simulator data.** The open-set safeguard is not reliable. See [docs/TRL.md](docs/TRL.md).

This repository reports that measurement only. Methods covered by filed patent claims are not described here.

The filing card for article registration and achievements is [docs/REGISTRATION.md](docs/REGISTRATION.md) (product id `hmitime`). The NPIC&HMIT and ISOFIC 2027 gate is [docs/JOURNAL_FIT.md](docs/JOURNAL_FIT.md). The note is [article/abstract.md](article/abstract.md). All three are rewritten from `outputs/results.json` by `python scripts/write_registration.py`. The article status on the card is unsubmitted.

The filing card for article registration and achievements is [docs/REGISTRATION.md](docs/REGISTRATION.md) (product id `hmitime`). The NPIC&HMIT and ISOFIC 2027 gate is [docs/JOURNAL_FIT.md](docs/JOURNAL_FIT.md). The note is [article/abstract.md](article/abstract.md). All three are rewritten from `outputs/results.json` by `python scripts/write_registration.py`. The article status on the card is unsubmitted.

## Run
```
pip install -r requirements.txt
python -m pytest -q tests
python scripts/run_experiment.py     # downloads data/runs on first use (needs the gh CLI), writes outputs/results.json
python scripts/write_registration.py  # rewrites the filing card, journal-fit note, and abstract from that file
python scripts/write_registration.py  # rewrites the filing card, journal-fit note, and abstract from that file
```

## Measured results (alpha = 0.05, 10 random run-level splits, 316 runs, 12 types)
| window after insertion | accuracy | coverage | single type shown | single and correct |
|---|---|---|---|---|
| 20-60 s | 0.263 | 0.963 | 0.088 | 0.088 |
| 90 s | 0.966 | 0.963 | 0.950 | 0.941 |
| 120 s | 0.954 | 0.959 | 0.944 | 0.925 |
| 300 s | 0.935 | 0.961 | 0.834 | 0.812 |
| 600 s | 0.904 | 0.959 | 0.833 | 0.810 |

- A correct single diagnosis was shown by 120 s in 95.8 % of test runs; 3.5 % were never resolved within 600 s.
- Open set, conformal empty set (window 300 s, 5 splits): 2.7 % of held-out runs gave an empty set (NO_MATCH) and 68.1 % received a single wrong type. The NO_MATCH state is therefore **not** a reliable safeguard.

Open-set scores, same leave-one-type-out splits. A run is flagged when its score exceeds the threshold fit on known calibration runs (target false-reject 5 %). Means are over the 12 held-out types:

| window | score | unknown detected | known rejected | AUROC |
|---|---|---|---|---|
| 90 s | Mahalanobis | 0.267 | 0.033 | 0.674 |
| 90 s | energy | 0.061 | 0.033 | 0.560 |
| 120 s | Mahalanobis | 0.203 | 0.028 | 0.635 |
| 120 s | energy | 0.046 | 0.021 | 0.560 |
| 300 s | Mahalanobis | 0.110 | 0.056 | 0.615 |
| 300 s | energy | 0.065 | 0.023 | 0.513 |

At 300 s the Mahalanobis AUROC ranges from 0.090 (MD, none detected) to 0.869 (RW). The energy AUROC ranges from 0.137 (LOCA) to 0.955 (LR). Neither score is a reliable substitute for NO_MATCH.

Full numbers: `outputs/results.json`.

## Limits
Simulator data from one PWR model, not plant data; 12 of the 18 published accident types are available as CSV; the SLBIC type has only 9 usable runs (files with extra columns or too few rows are skipped); no operator study; not a safety-classified function.

Data: NPPAD (Tsinghua / thu-inet), downloaded at run time, not stored here.
