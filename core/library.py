"""
Library — the central class holding all data and business rules.

Data structures (LO1):
    books         dict[str, Book]          ISBN -> Book, O(1) lookup
    members       dict[str, Member]        member_id -> Member, O(1) lookup
    loans         list[Loan]               full loan history, in issue order
    reservations  dict[str, deque[str]]    ISBN -> FIFO queue of member_ids

Both cli_app.py and gui_app.py call ONLY the public methods below, so all
validation and rules live in one place (NFR3). Nothing here prints, asks for
input or uses tkinter: problems are reported by raising the exceptions in
core/exceptions.py.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Deque, Dict, List, Optional

from core.exceptions import NotFoundError, UnavailableError, ValidationError
from core.models import Book, Loan, Member

LOAN_PERIOD_DAYS = 14      # standard loan length
FINE_PER_DAY = 0.20        # £ per day overdue
MAX_LOANS_PER_MEMBER = 3   # business rule
MIN_YEAR = 1000            # earliest publication year accepted (FR1)

MEMBER_ID_PATTERN = re.compile(r"^M\d{3}$")


def clean_isbn(isbn: str) -> str:
    """Return ``isbn`` with surrounding whitespace, inner spaces and hyphens removed."""
    return str(isbn).strip().replace("-", "").replace(" ", "")


def validate_isbn(isbn: str) -> str:
    """Validate an ISBN-13 and return it in normalised (digits only) form (FR1).

    Spaces and hyphens are ignored. The ISBN must then be exactly 13 digits
    and pass the ISBN-13 checksum: digits are weighted 1, 3, 1, 3, ... and the
    weighted sum of all 13 digits must be divisible by 10.

    Raises:
        ValidationError: if the ISBN is malformed or the checksum is wrong.
    """
    digits = clean_isbn(isbn)
    if len(digits) != 13 or not digits.isdigit():
        raise ValidationError("ISBN must be 13 digits (spaces and hyphens are allowed).")
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    if total % 10 != 0:
        raise ValidationError(f"ISBN {digits} has an invalid checksum.")
    return digits


def normalise_member_id(member_id: str) -> str:
    """Return ``member_id`` stripped and upper-cased (so 'm004' matches 'M004')."""
    return str(member_id).strip().upper()


class Library:
    """In-memory library with books, members, loans and reservations."""

    def __init__(self) -> None:
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.loans: List[Loan] = []
        self.reservations: Dict[str, Deque[str]] = {}

    # ---- Lookup helpers (NFR5: O(1) dict access) ---------------------------
    def get_book(self, isbn: str) -> Book:
        """Return the book with this ISBN, or raise NotFoundError."""
        book = self.books.get(clean_isbn(isbn))
        if book is None:
            raise NotFoundError(f"No book with ISBN {clean_isbn(isbn) or '(blank)'}.")
        return book

    def get_member(self, member_id: str) -> Member:
        """Return the member with this ID, or raise NotFoundError."""
        member = self.members.get(normalise_member_id(member_id))
        if member is None:
            raise NotFoundError(f"No member with ID {normalise_member_id(member_id) or '(blank)'}.")
        return member

    # ---- Books (FR1, FR2) -------------------------------------------------
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int = 1) -> Book:
        """Add a new book title with ``copies`` copies (FR1).

        Raises:
            ValidationError: invalid ISBN, duplicate ISBN, blank title/author,
                year outside 1000..current year, or copies < 1.
        """
        isbn = validate_isbn(isbn)
        if isbn in self.books:
            raise ValidationError(f"A book with ISBN {isbn} already exists.")
        title = str(title).strip()
        author = str(author).strip()
        if not title:
            raise ValidationError("Title must not be empty.")
        if not author:
            raise ValidationError("Author must not be empty.")
        current_year = date.today().year
        if not isinstance(year, int) or isinstance(year, bool) or not MIN_YEAR <= year <= current_year:
            raise ValidationError(f"Year must be a whole number from {MIN_YEAR} to {current_year}.")
        if not isinstance(copies, int) or isinstance(copies, bool) or copies < 1:
            raise ValidationError("Number of copies must be at least 1.")

        book = Book(isbn, title, author, year, total_copies=copies, available_copies=copies)
        self.books[isbn] = book
        return book

    def remove_book(self, isbn: str) -> None:
        """Remove a book title and its reservation queue (FR2).

        Raises:
            NotFoundError: unknown ISBN.
            UnavailableError: one or more copies are still on loan.
        """
        book = self.get_book(isbn)
        if book.available_copies < book.total_copies:
            on_loan = book.total_copies - book.available_copies
            raise UnavailableError(
                f"Cannot remove '{book.title}': {on_loan} cop{'y is' if on_loan == 1 else 'ies are'} on loan."
            )
        del self.books[book.isbn]
        self.reservations.pop(book.isbn, None)

    # ---- Members (FR3) ----------------------------------------------------
    def register_member(self, member_id: str, name: str) -> Member:
        """Register a new member (FR3).

        Raises:
            ValidationError: ID not in the form M + 3 digits (e.g. M004),
                duplicate ID, or blank name.
        """
        member_id = normalise_member_id(member_id)
        if not MEMBER_ID_PATTERN.match(member_id):
            raise ValidationError("Member ID must be 'M' followed by 3 digits, e.g. M004.")
        if member_id in self.members:
            raise ValidationError(f"Member ID {member_id} is already registered.")
        name = str(name).strip()
        if not name:
            raise ValidationError("Member name must not be empty.")
        member = Member(member_id, name)
        self.members[member_id] = member
        return member

    def list_members(self) -> List[Member]:
        """Return all members ordered by member ID."""
        return [self.members[key] for key in sorted(self.members)]

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
