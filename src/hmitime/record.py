"""Article and achievement card for HMI-Timing.

Measured rows are formatted from outputs/results.json. The article row stays
unsubmitted: a patent attorney has not reviewed the text.
"""

from __future__ import annotations

REPO = "https://github.com/parsasohrab1/articles-npp-hmi-timing"
BRANCH = "feat/npp-hmi-timing-realdata"
PULL = "https://github.com/parsasohrab1/articles-npp-hmi-timing/pull/3"
TITLE = "Time to a certified diagnosis on simulated NPPAD accident runs"
CALL = "NPIC&HMIT and ISOFIC 2027"
CALL_PAGE = "https://www.ans.org/meetings/npichmitisofic2027/"
CALL_FILE = "https://www.ans.org/meetings/file/view-1670/"


def _r3(value: float) -> str:
    return f"{float(value):.3f}"


def _mean(block: dict, key: str) -> str:
    return _r3(block[key][0])


def _ends(rows: list[dict]) -> tuple[dict, dict]:
    ordered = sorted(rows, key=lambda row: row["auroc"])
    return ordered[0], ordered[-1]


def registration_markdown(results: dict) -> str:
    """Internal filing card. Numbers come only from `results`."""
    closed = results["closed_set"]["alpha_0.05"]
    timing = closed["first_correct_singleton_s"]
    windows = closed["by_window"]
    opened = results["open_set"]
    scores = results["open_set_scores"]["by_window"]
    lines = [
        "| پنجره (ثانیه) | دقت | پوشش | تک‌نوعِ درست |",
        "|---|---|---|---|",
    ]
    for name in ("90", "120", "300", "600"):
        row = windows[name]
        lines.append(
            f"| {name} | {_mean(row, 'accuracy')} | {_mean(row, 'coverage')} | "
            f"{_mean(row, 'singleton_correct')} |"
        )
    score_lines = [
        "| پنجره (ثانیه) | امتیاز | تشخیص نوع دیده‌نشده | رد نوع شناخته‌شده | AUROC |",
        "|---|---|---|---|---|",
    ]
    for name in ("90", "120", "300"):
        for kind, label in (("mahalanobis", "ماهالانوبیس"), ("energy", "انرژی")):
            row = scores[name][kind]
            score_lines.append(
                f"| {name} | {label} | {_r3(row['mean_unknown_detect'])} | "
                f"{_r3(row['mean_known_reject'])} | {_r3(row['mean_auroc'])} |"
            )
    low_m, high_m = _ends(scores["300"]["mahalanobis"]["per_type"])
    low_e, high_e = _ends(scores["300"]["energy"]["per_type"])
    table = "\n".join(lines)
    score_table = "\n".join(score_lines)
    return f"""# ثبت مقاله و دستاوردها

شناسه محصول: `hmitime`. این برگه برای ثبت داخلی است. مقاله‌ای ارسال نشده است.

| قلم | ثبت |
|---|---|
| محصول | HMI-Timing |
| ریپو | {REPO} |
| شاخه | `{BRANCH}` |
| پیش‌نویس بررسی | {PULL} |
| بلوغ | TRL 4 برای زمان تشخیص روی شبیه‌ساز؛ دروازه‌ی مجموعه‌ی باز تأیید نشده |
| نوع داده | شبیه‌ساز PWR (NPPAD، نه اندازه‌گیری نیروگاه) |
| داده | NPPAD، مخزن عمومی thu-inet/NuclearPowerPlantAccidentData |
| عنوان یادداشت | {TITLE} |
| متن | `article/abstract.md` |
| دروازه ژورنال | `docs/JOURNAL_FIT.md` |
| وضعیت مقاله | ارسال نشده |
| فراخوان بررسی‌شده | {CALL}؛ مهلت چکیده ۲۰ نوامبر ۲۰۲۶ |
| وکیل پتنت | متن ارسال را تأیید نکرده است. این برگه روش مشمول ادعای ثبت‌شده را شرح نمی‌دهد. |

## دستاورد اندازه‌گیری‌شده

منبع اعداد: `outputs/results.json`، گردشده به سه رقم اعشار. تعداد ران: {results["n_runs"]}. تعداد نوع: {len(results["types"])}. آلفا: {_r3(opened["alpha"])}. ران‌های SLBIC: {results["runs_per_type"]["SLBIC"]}.

{table}

سهم ران‌های آزمون با تک‌نوع درست تا ۱۲۰ ثانیه: {_r3(timing["share_resolved_by_120s"])}. سهم بدون تک‌نوع درست تا ۶۰۰ ثانیه: {_r3(timing["share_never_resolved_by_600s"])}.

مجموعه‌ی باز کانفرمال در پنجره‌ی {opened["window_s"]} ثانیه: تهی {_r3(opened["mean_unknown_empty"])}، تک‌نوع غلط {_r3(opened["mean_unknown_singleton_wrong"])}، تهی روی نوع شناخته‌شده {_r3(opened["mean_known_empty"])}.

{score_table}

در ۳۰۰ ثانیه AUROC ماهالانوبیس از {_r3(low_m["auroc"])} ({low_m["held_out"]}) تا {_r3(high_m["auroc"])} ({high_m["held_out"]}) است. AUROC انرژی از {_r3(low_e["auroc"])} ({low_e["held_out"]}) تا {_r3(high_e["auroc"])} ({high_e["held_out"]}) است.

دستاورد ثبت‌شده زمان رسیدن به تشخیص تک‌نوع درست روی شبیه‌ساز است، و ناموفق بودن مجموعه‌ی خالی، ماهالانوبیس، و انرژی به‌عنوان دروازه‌ی نوع دیده‌نشده.
"""


def abstract_markdown(results: dict) -> str:
    """Three-paragraph note. It is not a submission."""
    closed = results["closed_set"]["alpha_0.05"]
    timing = closed["first_correct_singleton_s"]
    at_90 = closed["by_window"]["90"]
    opened = results["open_set"]
    at_300 = results["open_set_scores"]["by_window"]["300"]
    at_90_score = results["open_set_scores"]["by_window"]["90"]["mahalanobis"]
    distance = at_300["mahalanobis"]
    energy = at_300["energy"]
    return f"""# Abstract

A display aid was timed on the public NPPAD simulator (a PCTRAN-style PWR; not plant measurements). {results["n_runs"]} runs of {len(results["types"])} accident types were split by run. A random forest at each window produced a split-conformal set at alpha {_r3(opened["alpha"])}. The display names one type only when that set has one member. A correct singleton was reached by 120 s on {_r3(timing["share_resolved_by_120s"])} of test runs, and {_r3(timing["share_never_resolved_by_600s"])} of test runs had none by 600 s. At 90 s, accuracy was {_mean(at_90, "accuracy")} and the share with a correct singleton was {_mean(at_90, "singleton_correct")}.

One accident type was then held out of training and calibration. At {opened["window_s"]} s the conformal set was empty on {_r3(opened["mean_unknown_empty"])} of those runs and held exactly one wrong type on {_r3(opened["mean_unknown_singleton_wrong"])}. A minimum class-conditional Mahalanobis distance and a multinomial-logistic energy, both in a fixed 10-component subspace, were calibrated on the known runs. At 300 s the Mahalanobis score flagged {_r3(distance["mean_unknown_detect"])} of held-out runs (known reject {_r3(distance["mean_known_reject"])}, AUROC {_r3(distance["mean_auroc"])}). The energy score flagged {_r3(energy["mean_unknown_detect"])} (known reject {_r3(energy["mean_known_reject"])}, AUROC {_r3(energy["mean_auroc"])}). At 90 s the Mahalanobis AUROC was {_r3(at_90_score["mean_auroc"])}. Neither score reliably marks an accident type that was absent from training.

The evidence is one simulated PWR model, with no operator study and no safety classification. This note is not submitted. A patent attorney has not reviewed it, and it does not describe methods covered by filed patent claims. Numbers are rounded from `outputs/results.json`.
"""


def journal_fit_markdown(results: dict) -> str:
    """Gate record for the checked call. Nothing has been uploaded."""
    opened = results["open_set"]
    timing = results["closed_set"]["alpha_0.05"]["first_correct_singleton_s"]
    distance = results["open_set_scores"]["by_window"]["300"]["mahalanobis"]
    energy = results["open_set_scores"]["by_window"]["300"]["energy"]
    return f"""# Journal fitness — {CALL}

Call checked: 15th NPIC&HMIT jointly with the 9th ISOFIC, 9–13 May 2027, Salt Lake City.

| Item | Record |
|---|---|
| Call page | {CALL_PAGE} |
| Call file | {CALL_FILE} |
| Organizers | ANS Human Factors, Instrumentation & Controls Division, with the Korean Nuclear Society |
| Abstract deadline | 20 November 2026 |
| Full paper, if the abstract is accepted | 29 January 2027; at most 10 pages before page charges |
| Abstract shape | One page, three paragraphs, fewer than 500 words |
| Checked | 7 November 2026 |

| Item | What the call page says |
|---|---|
| Scope | Nuclear instrumentation and control, human factors, cybersecurity, artificial intelligence and machine learning, and advanced modeling. |
| Nearby topics | HF3 (human factors for AI/ML), HF9 (operator aids), IC15 (machine learning for nuclear). |
| Publication | Peer-reviewed proceedings. An accepted paper must be presented. |

## Fit

The question is when a display may show one accident type, which sits next to HF9 and HF3. The evidence is the NPPAD simulator, not an operator study (HF12) and not a plant I&C system. {results["n_runs"]} simulated runs, {len(results["types"])} accident types.

## Evidence

Correct singleton by 120 s: {_r3(timing["share_resolved_by_120s"])}. None by 600 s: {_r3(timing["share_never_resolved_by_600s"])}. At {opened["window_s"]} s the held-out conformal set is empty on {_r3(opened["mean_unknown_empty"])} of runs. Mahalanobis AUROC {_r3(distance["mean_auroc"])}. Energy AUROC {_r3(energy["mean_auroc"])}. Full rows are on the filing card.

## Decision

Do not upload. The abstract deadline is still open on the check date. Submission stays closed because a patent attorney has not confirmed that the text discloses no claimed method. The note in [../article/abstract.md](../article/abstract.md) is not a submission. The internal filing card is [REGISTRATION.md](REGISTRATION.md).
"""
