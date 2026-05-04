"""Data IO helpers for ClaraCare Sprint 2."""

from pathlib import Path
from typing import Iterable

import jsonlines


def load_jsonl(path: Path) -> list[dict]:
    """Load JSONL records into a list."""
    assert path.exists(), f"Missing file: {path}"
    with jsonlines.open(path) as reader:
        rows = list(reader)
    assert rows, f"No rows found in {path}"
    return rows


def save_jsonl(path: Path, rows: Iterable[dict]) -> None:
    """Write iterable of dict records to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    with jsonlines.open(path, mode="w") as writer:
        writer.write_all(rows)
    assert path.exists(), f"Failed to save {path}"


def assert_columns(rows: list[dict], required: list[str]) -> None:
    """Fail loudly if any required columns are missing."""
    assert rows and isinstance(rows[0], dict), "rows must be a non-empty list[dict]"
    missing = [col for col in required if col not in rows[0]]
    assert not missing, f"Missing columns: {missing}"


def count_jsonl(path: Path) -> int:
    """Return number of rows in a JSONL file."""
    with jsonlines.open(path) as reader:
        return sum(1 for _ in reader)
