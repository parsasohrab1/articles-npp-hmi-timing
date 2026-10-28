# HMI-Timing – Software Requirements Specification

## 1. Purpose
Quantify, on public simulator data, **how many seconds after an accident begins** a data-driven diagnosis aid can show an operator a *statistically certified* answer, and what the display should show before that moment.

## 2. Scope
Offline research tool. It is **not** a safety-classified system and is not connected to any plant. Input: multivariate plant-variable time series (NPPAD simulated PWR runs, 10 s sampling). Output: per-window prediction sets, display mode, and time-to-certified-singleton statistics.

## 3. Functional requirements
| ID | Requirement |
|----|-------------|
| FR-1 | Load runs of 12 accident types and cut windows ending 20–600 s after accident insertion. |
| FR-2 | Build features per window (change from pre-accident state, last-30-s slope, running maximum change). |
| FR-3 | Train a classifier on a training split; calibrate a split-conformal threshold on a disjoint calibration split of runs. |
| FR-4 | Emit a prediction set per window; map it to a display mode: SINGLE, CANDIDATES, NO_MATCH. |
| FR-5 | Report per window: accuracy, coverage, mean set size, singleton share, empty-set share. |
| FR-6 | Report the first window at which a correct singleton is shown (time-to-certified-diagnosis). |
| FR-7 | Open-set test: hold one accident type out of training and calibration and report how often the display answers NO_MATCH instead of a wrong SINGLE. |
| FR-8 | Splits are by run (no run appears in two splits); repeated over random seeds. |

## 4. Non-functional requirements
- NFR-1 Reproducible: one command regenerates `outputs/results.json`; seeds fixed.
- NFR-2 Raw data not stored in the repository; downloaded from the public source.
- NFR-3 Only measured numbers are reported; no plant data claims.

## 5. Constraints and known limits
- Simulator data (PCTRAN-style PWR), not plant data; 12 of the 18 published accident types are available as CSV.
- Single reactor model; no sensor faults, no operator actions after insertion.
- Split-conformal coverage is marginal, not per-type.
