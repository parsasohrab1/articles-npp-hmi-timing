"""Rewrite the filing card, the journal-fit note, and the abstract from outputs/results.json.

Usage: python scripts/write_registration.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmitime.record import (
    abstract_markdown,
    journal_fit_markdown,
    registration_markdown,
)


def main() -> None:
    payload = json.loads((ROOT / "outputs" / "results.json").read_text(encoding="utf-8"))
    targets = {
        ROOT / "docs" / "REGISTRATION.md": registration_markdown(payload),
        ROOT / "docs" / "JOURNAL_FIT.md": journal_fit_markdown(payload),
        ROOT / "article" / "abstract.md": abstract_markdown(payload),
    }
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(path)


if __name__ == "__main__":
    main()
