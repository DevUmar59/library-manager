"""
File reading and writing for the Library Loans Manager (FR10, NFR6).

Data is stored as a single JSON file:

    {
        "books":        [ {Book.to_dict()}, ... ],
        "members":      [ {Member.to_dict()}, ... ],
        "loans":        [ {Loan.to_dict()}, ... ],
        "reservations": { "<isbn>": ["<member_id>", ...] }
    }

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from core.exceptions import LibraryError

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "library_data.json"
SAMPLE_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"

# Top-level keys and the JSON type each one must have.
REQUIRED_KEYS = {"books": list, "members": list, "loans": list, "reservations": dict}


def empty_data() -> dict:
    """Return a new, empty data dictionary in the storage format."""
    return {"books": [], "members": [], "loans": [], "reservations": {}}


def load_data(path: Path = DEFAULT_DATA_FILE) -> dict:
    """Load and return the raw data dictionary from a JSON file (FR10).

    If the file does not exist, return an empty structure.

    Raises:
        LibraryError: if the file cannot be read, is not valid JSON, or does
            not contain the expected top-level keys.
    """
    path = Path(path)
    if not path.exists():
        return empty_data()
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LibraryError(f"Data file {path.name} is not valid JSON: {exc.msg} (line {exc.lineno})") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise LibraryError(f"Could not read data file {path.name}: {exc}") from exc

    if not isinstance(data, dict):
        raise LibraryError(f"Data file {path.name} must contain a JSON object at the top level.")
    for key, expected_type in REQUIRED_KEYS.items():
        if key not in data:
            raise LibraryError(f"Data file {path.name} is missing the '{key}' section.")
        if not isinstance(data[key], expected_type):
            raise LibraryError(
                f"Section '{key}' in {path.name} must be a JSON {expected_type.__name__}."
            )
    return data


def save_data(data: dict, path: Path = DEFAULT_DATA_FILE) -> None:
    """Write the data dictionary to a JSON file safely (NFR6).

    The data is first written to ``<path>.tmp`` and then moved over the real
    file with ``os.replace`` (atomic on the same filesystem), so a crash part
    way through writing can never leave a half-written data file.

    Raises:
        LibraryError: if the file cannot be written.
    """
    path = Path(path)
    tmp_path = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    except OSError as exc:
        raise LibraryError(f"Could not save data to {path.name}: {exc}") from exc
