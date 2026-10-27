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
from collections import deque
from datetime import date, timedelta
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
        """Lend one copy of a book to a member (FR4).

        The due date is ``today + LOAN_PERIOD_DAYS``.

        Raises:
            NotFoundError: unknown ISBN or member.
            UnavailableError: no copies available, member already has
                MAX_LOANS_PER_MEMBER active loans, or already holds this book.
        """
        today = today or date.today()
        book = self.get_book(isbn)
        member = self.get_member(member_id)
        member_loans = self.active_loans(member.member_id)
        if any(loan.isbn == book.isbn for loan in member_loans):
            raise UnavailableError(f"{member.name} already has '{book.title}' on loan.")
        if len(member_loans) >= MAX_LOANS_PER_MEMBER:
            raise UnavailableError(
                f"{member.name} already has {MAX_LOANS_PER_MEMBER} books on loan (the maximum)."
            )
        if book.available_copies <= 0:
            raise UnavailableError(f"No copies of '{book.title}' are available. You can reserve it.")
        # FR6: while a reservation queue exists, only the member at the front may borrow.
        queue = self.reservations.get(book.isbn)
        if queue:
            if queue[0] != member.member_id:
                raise UnavailableError(
                    f"'{book.title}' is reserved; member {queue[0]} is first in the queue."
                )
            queue.popleft()
            if not queue:
                del self.reservations[book.isbn]

        loan =Loan(book.isbn, member.member_id, today, today + timedelta(days=LOAN_PERIOD_DAYS))
        self.loans.append(loan)
        book.available_copies -= 1
        return loan

    def return_book(self, isbn: str, member_id: str, today: Optional[date] = None) -> float:
        """Return the book and the fine owed (0.0 if on time) (FR5).

        Raises:
            NotFoundError: this member has no active loan of this book.
        """
        today = today or date.today()
        isbn = clean_isbn(isbn)
        member_id = normalise_member_id(member_id)
        loan = next(
            (l for l in self.active_loans(member_id) if l.isbn == isbn),
            None,
        )
        if loan is None:
            raise NotFoundError(f"Member {member_id} has no active loan of ISBN {isbn}.")
        loan.return_date = today
        book = self.books.get(isbn)
        if book is not None:
            book.available_copies = min(book.available_copies + 1, book.total_copies)
        return self.calculate_fine(loan, today)

    def active_loans(self, member_id: Optional[str] = None) -> List[Loan]:
        """Return loans not yet returned, optionally only those of one member."""
        wanted = normalise_member_id(member_id) if member_id is not None else None
        return [
            loan for loan in self.loans
            if not loan.is_returned and (wanted is None or loan.member_id == wanted)
        ]

    # ---- Reservations (FR6) -----------------------------------------------
    def reserve_book(self, isbn: str, member_id: str) -> int:
        """Add member to the book's FIFO queue; return their position (FR6).

        Positions are 1-based. Appending to a deque is O(1), and so is
        removing the front member when they borrow the book.

        Raises:
            NotFoundError: unknown ISBN or member.
            UnavailableError: a copy is available (issue it instead) or the
                member already holds this book.
            ValidationError: the member is already in this book's queue.
        """
        book = self.get_book(isbn)
        member = self.get_member(member_id)
        if book.available_copies > 0:
            raise UnavailableError(
                f"'{book.title}' has {book.available_copies} cop{'y' if book.available_copies == 1 else 'ies'} "
                "available. Issue it instead of reserving."
            )
        if any(loan.isbn == book.isbn for loan in self.active_loans(member.member_id)):
            raise UnavailableError(f"{member.name} already has '{book.title}' on loan.")
        queue = self.reservations.setdefault(book.isbn, deque())
        if member.member_id in queue:
            raise ValidationError(f"{member.name} has already reserved '{book.title}'.")
        queue.append(member.member_id)
        return len(queue)

    def next_in_queue(self, isbn: str) -> Optional[str]:
        """Return the member ID at the front of a book's queue, or None (FR6)."""
        queue = self.reservations.get(clean_isbn(isbn))
        return queue[0] if queue else None

    def reservation_queue(self, isbn: str) -> List[str]:
        """Return a copy of a book's reservation queue, front first (FR6)."""
        return list(self.reservations.get(clean_isbn(isbn), ()))

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
        """Return the fine for a loan: days late x FINE_PER_DAY, to 2 dp (FR5, FR9).

        A returned loan is measured to its return date, an active loan to
        ``today``. The fine is never negative (returning early costs nothing).
        """
        end = loan.return_date or today or date.today()
        days_late = max(0, (end - loan.due_date).days)
        return round(days_late * FINE_PER_DAY, 2)

    # ---- Persistence (FR10) ----------------------------------------------
    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Library":
        raise NotImplementedError
