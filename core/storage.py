"""
File reading and writing for the Library Loans Manager.

Data is stored as a single JSON file:

    {
        "books":        [ {Book.to_dict()}, ... ],
        "members":      [ {Member.to_dict()}, ... ],
        "loans":        [ {Loan.to_dict()}, ... ],
        "reservations": { "<isbn>": ["<member_id>", ...] }
    }

STATUS: starter stubs — implemented in the `feature/core` branch.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "library_data.json"
SAMPLE_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"


def load_data(path: Path = DEFAULT_DATA_FILE) -> dict:
    """Load and return the raw data dictionary from a JSON file.

    If the file does not exist, return an empty structure.
    If the file is corrupt, raise core.exceptions.LibraryError.
    """
    # TODO (feature/core)
    raise NotImplementedError("load_data will be implemented in feature/core")


def save_data(data: dict, path: Path = DEFAULT_DATA_FILE) -> None:
    """Write the data dictionary to a JSON file safely (write temp file, then replace)."""
    # TODO (feature/core)
    raise NotImplementedError("save_data will be implemented in feature/core")
