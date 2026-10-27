"""
Data models for the Library Loans Manager.

Each model is a dataclass with to_dict()/from_dict() so it can be saved to and
loaded from JSON by core/storage.py.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional


@dataclass
class Book:
    """A book title held by the library (may have several copies)."""

    isbn: str
    title: str
    author: str
    year: int
    total_copies: int = 1
    available_copies: int = 1

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        return cls(**data)


@dataclass
class Member:
    """A registered library member. Use fictional data only (no real people)."""

    member_id: str
    name: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        return cls(**data)


@dataclass
class Loan:
    """One copy of a book lent to one member."""

    isbn: str
    member_id: str
    issue_date: date
    due_date: date
    return_date: Optional[date] = None

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "member_id": self.member_id,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Loan":
        return cls(
            isbn=data["isbn"],
            member_id=data["member_id"],
            issue_date=date.fromisoformat(data["issue_date"]),
            due_date=date.fromisoformat(data["due_date"]),
            return_date=(
                date.fromisoformat(data["return_date"]) if data.get("return_date") else None
            ),
        )
