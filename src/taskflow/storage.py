"""
JSON persistence layer.

Isolating file I/O in its own class keeps TaskManager free of filesystem
concerns and makes it easy to swap storage backends (e.g. CSV, SQLite)
later without touching business logic.
"""

from __future__ import annotations

import json
import os
from typing import List

from taskflow.exceptions import StorageError


class JSONStorage:
    """Reads and writes a list of task dictionaries to a JSON file."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        directory = os.path.dirname(self.filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def load(self) -> List[dict]:
        """Return list of task dicts, or [] if file doesn't exist yet."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
        except (json.JSONDecodeError, OSError) as exc:
            raise StorageError(f"Failed to read data file '{self.filepath}': {exc}") from exc

        if not isinstance(data, list):
            raise StorageError(f"Data file '{self.filepath}' is corrupted (expected a list).")
        return data

    def save(self, records: List[dict]) -> None:
        """Write task dicts to disk atomically (write to temp file, then replace)."""
        tmp_path = f"{self.filepath}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            os.replace(tmp_path, self.filepath)
        except OSError as exc:
            raise StorageError(f"Failed to save data file '{self.filepath}': {exc}") from exc
