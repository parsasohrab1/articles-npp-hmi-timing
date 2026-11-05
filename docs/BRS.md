# Business Requirements Specification (BRS)

**Product:** HMI-Timing (articles-npp-hmi-timing)
*Reconstructed from the README, the requirements document, the TRL assessment and the tests of this repository. Not reviewed by the owner. A patent attorney must review before publication of method details.*

## 1. Business problem
After a nuclear-plant accident starts, an operator aid can show a diagnosis only once the data are informative. The question is how soon a certified diagnosis can be shown, and what the display should show before that or for an unknown accident.

## 2. Business objectives
| ID | Objective |
|----|-----------|
| BO-1 | Measure the time until a correct single diagnosis can be shown with a stated confidence |
| BO-2 | Define display states (single, candidates, no match) |
| BO-3 | Test the behaviour for an accident type that was not seen in calibration |

## 3. Users and stakeholders (proposed; to be confirmed by the owner)
Human-factors and control-room designers; nuclear-safety researchers.

## 4. Scope
In scope: run-level conformal diagnosis on the public NPPAD simulator data.
Out of scope: use in a real control room, licensing, other plant designs.

## 5. Constraints and assumptions
- All data are synthetic or public benchmark data; the product makes no clinical, operational or regulatory claim.
- Maturity is TRL 4 (see docs/TRL.md).
- The open-set test showed that the no-match state is not a reliable safeguard in this setup (2.9% of withheld-type runs gave an empty set).

## 6. Success measures (to be measured on real data)
Time to first correct singleton, coverage, and the rate of no-match for withheld accident types, on other simulators or plants.
