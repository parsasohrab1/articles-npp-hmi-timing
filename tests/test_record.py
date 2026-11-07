import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hmitime.record import (
    abstract_markdown,
    journal_fit_markdown,
    registration_markdown,
)

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _results():
    return json.loads(_read(os.path.join(ROOT, "outputs", "results.json")))


def test_registration_card_matches_the_results_file():
    results = _results()
    card = _read(os.path.join(ROOT, "docs", "REGISTRATION.md"))
    note = _read(os.path.join(ROOT, "docs", "JOURNAL_FIT.md"))
    abstract = _read(os.path.join(ROOT, "article", "abstract.md"))
    assert card == registration_markdown(results)
    assert note == journal_fit_markdown(results)
    assert abstract == abstract_markdown(results)
    assert "ارسال نشده" in card
    assert "hmitime" in card
    assert "venue-fit gate" in note
    assert "This note is not submitted." in abstract


def test_abstract_is_inside_the_call_limit():
    abstract = _read(os.path.join(ROOT, "article", "abstract.md"))
    words = re.findall(r"[A-Za-z0-9'.-]+", abstract)
    assert 0 < len(words) < 500
