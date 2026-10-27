"""
core — shared business logic for the Library Loans Manager.

Both front ends (cli_app.py and gui_app.py) import from this package, so the
GUI is a new interface over the same logic rather than a rewrite.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from core.exceptions import (
    LibraryError,
    NotFoundError,
    UnavailableError,
    ValidationError,
)
from core.models import Book, Loan, Member

__all__ = [
    "Book",
    "Member",
    "Loan",
    "LibraryError",
    "NotFoundError",
    "UnavailableError",
    "ValidationError",
]
