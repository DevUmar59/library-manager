"""
Library — the central class holding all data and business rules.

Data structures (LO1):
    books         dict[str, Book]          ISBN -> Book, O(1) lookup
    members       dict[str, Member]        member_id -> Member, O(1) lookup
    loans         list[Loan]               full loan history, in issue order
    reservations  dict[str, deque[str]]    ISBN -> FIFO queue of member_ids

Both cli_app.py and gui_app.py call ONLY the public methods below, so all
validation and rules live in one place.

STATUS: starter stubs — implemented in the `feature/core` branch.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from datetime import date
from typing import Deque, Dict, List, Optional

from core.models import Book, Loan, Member

LOAN_PERIOD_DAYS = 14      # standard loan length
FINE_PER_DAY = 0.20        # £ per day overdue
MAX_LOANS_PER_MEMBER = 3   # business rule


class Library:
    """In-memory library with books, members, loans and reservations."""

    def __init__(self) -> None:
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.loans: List[Loan] = []
        self.reservations: Dict[str, Deque[str]] = {}

    # ---- Books (FR1, FR2) -------------------------------------------------
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int = 1) -> Book:
        raise NotImplementedError

    def remove_book(self, isbn: str) -> None:
        raise NotImplementedError

    # ---- Members (FR3) ----------------------------------------------------
    def register_member(self, member_id: str, name: str) -> Member:
        raise NotImplementedError

    # ---- Loans (FR4, FR5) -------------------------------------------------
    def issue_book(self, isbn: str, member_id: str, today: Optional[date] = None) -> Loan:
        raise NotImplementedError

    def return_book(self, isbn: str, member_id: str, today: Optional[date] = None) -> float:
        """Return the book and the fine owed (0.0 if on time)."""
        raise NotImplementedError

    # ---- Reservations (FR6) -----------------------------------------------
    def reserve_book(self, isbn: str, member_id: str) -> int:
        """Add member to the book's FIFO queue; return their position."""
        raise NotImplementedError

    # ---- Search & sort (FR7, FR8) ----------------------------------------
    def search_books(self, query: str, field: str = "title") -> List[Book]:
        raise NotImplementedError

    def sorted_books(self, field: str = "title", reverse: bool = False) -> List[Book]:
        raise NotImplementedError

    # ---- Reports (FR9) ----------------------------------------------------
    def overdue_loans(self, today: Optional[date] = None) -> List[Loan]:
        raise NotImplementedError

    @staticmethod
    def calculate_fine(loan: Loan, today: Optional[date] = None) -> float:
        raise NotImplementedError

    # ---- Persistence (FR10) ----------------------------------------------
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Library":
        raise NotImplementedError
