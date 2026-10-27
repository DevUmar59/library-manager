"""
Custom exceptions for the Library Loans Manager.

Using our own exception types lets both front ends catch library errors and
show a friendly message, instead of crashing (supports NFR2: robustness).

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""


class LibraryError(Exception):
    """Base class for all expected library errors."""


class NotFoundError(LibraryError):
    """Raised when a book, member or loan does not exist."""


class ValidationError(LibraryError):
    """Raised when user input is invalid (empty title, bad ISBN, etc.)."""


class UnavailableError(LibraryError):
    """Raised when an action is not possible right now (e.g. no copies left)."""
