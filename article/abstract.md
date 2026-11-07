# Abstract

A display aid was timed on the public NPPAD simulator (a PCTRAN-style PWR; not plant measurements). 316 runs of 12 accident types were split by run. A random forest at each window produced a split-conformal set at alpha 0.050. The display names one type only when that set has one member. A correct singleton was reached by 120 s on 0.958 of test runs, and 0.035 of test runs had none by 600 s. At 90 s, accuracy was 0.966 and the share with a correct singleton was 0.941.

One accident type was then held out of training and calibration. At 300 s the conformal set was empty on 0.027 of those runs and held exactly one wrong type on 0.681. A minimum class-conditional Mahalanobis distance and a multinomial-logistic energy, both in a fixed 10-component subspace, were calibrated on the known runs. At 300 s the Mahalanobis score flagged 0.110 of held-out runs (known reject 0.056, AUROC 0.615). The energy score flagged 0.065 (known reject 0.023, AUROC 0.513). At 90 s the Mahalanobis AUROC was 0.674. Neither score reliably marks an accident type that was absent from training.

The evidence is one simulated PWR model, with no operator study and no safety classification. This note is not submitted. It does not describe methods covered by filed patent claims. Numbers are rounded from `outputs/results.json`.
