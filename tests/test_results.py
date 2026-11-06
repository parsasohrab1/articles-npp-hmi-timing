import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_results_json_records_the_open_set_scores():
    with open(os.path.join(ROOT, "outputs", "results.json"), encoding="utf-8") as handle:
        results = json.load(handle)
    assert results["n_runs"] == sum(results["runs_per_type"].values())
    assert "mean_unknown_empty" in results["open_set"]
    windows = results["open_set_scores"]["by_window"]
    assert set(windows) == {"90", "120", "300"}
    for window in windows.values():
        for kind in ("mahalanobis", "energy"):
            block = window[kind]
            assert len(block["per_type"]) == len(results["types"])
            for key in ("mean_unknown_detect", "mean_known_reject", "mean_auroc"):
                assert 0.0 <= block[key] <= 1.0
