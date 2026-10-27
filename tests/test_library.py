"""
Unit tests for core/library.py (FR1-FR9 business rules).

All date-dependent tests pass fixed dates, never the real "today", so the
results are the same whenever the tests are run.

Run all tests:  python -m unittest discover -s tests -v

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

import unittest
from datetime import date, timedelta

from core.exceptions import NotFoundError, UnavailableError, ValidationError
from core.library import (
    FINE_PER_DAY,
    LOAN_PERIOD_DAYS,
    MAX_LOANS_PER_MEMBER,
    Library,
    validate_isbn,
)

# Fictional test data (valid ISBN-13s).
PRIDE = "9780141439518"
GREAT = "9780141439570"
FRANK = "9780141439846"
JANE = "9780141441146"
EMMA = "9780141439471"
NEW_ISBN = "9780306406157"

ISSUE_DAY = date(2026, 3, 1)
DUE_DAY = ISSUE_DAY + timedelta(days=LOAN_PERIOD_DAYS)


def make_library() -> Library:
    """Return a small library with five books and three members."""
    library = Library()
    library.add_book(PRIDE, "Pride and Prejudice", "Jane Austen", 1813, 2)
    library.add_book(GREAT, "Great Expectations", "Charles Dickens", 1861, 1)
    library.add_book(FRANK, "Frankenstein", "Mary Shelley", 1818, 3)
    library.add_book(JANE, "Jane Eyre", "Charlotte Bronte", 1847, 1)
    library.add_book(EMMA, "Emma", "Jane Austen", 1815, 1)
    library.register_member("M001", "Alice Example")
    library.register_member("M002", "Bob Sample")
    library.register_member("M003", "Chen Test")
    return library


class TestIsbnValidation(unittest.TestCase):
    """FR1: ISBN-13 format and checksum."""

    def test_valid_isbn_with_hyphens_is_normalised(self):
        self.assertEqual(validate_isbn("978-0-306-40615-7"), NEW_ISBN)

    def test_invalid_checksum_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_isbn("9780306406158")

    def test_wrong_length_or_letters_rejected(self):
        for bad in ("978030640615", "97803064061577", "97803064061X7", ""):
            with self.subTest(isbn=bad), self.assertRaises(ValidationError):
                validate_isbn(bad)


class TestBooks(unittest.TestCase):
    """FR1 add book, FR2 remove book."""

    def setUp(self):
        self.library = make_library()

    def test_add_book_sets_available_copies_to_total(self):
        book = self.library.add_book(NEW_ISBN, "Test Book", "A. Writer", 2001, 4)
        self.assertEqual((book.total_copies, book.available_copies), (4, 4))
        self.assertIs(self.library.get_book(NEW_ISBN), book)

    def test_add_duplicate_isbn_rejected(self):
        with self.assertRaises(ValidationError):
            self.library.add_book(PRIDE, "Copy", "Someone", 2000)

    def test_add_book_blank_title_or_author_rejected(self):
        with self.assertRaises(ValidationError):
            self.library.add_book(NEW_ISBN, "   ", "Author", 2000)
        with self.assertRaises(ValidationError):
            self.library.add_book(NEW_ISBN, "Title", "", 2000)

    def test_year_boundaries_1000_and_current_year_accepted(self):
        self.library.add_book(NEW_ISBN, "Old", "Anon", 1000)
        self.library.add_book("9780000000002", "New", "Anon", date.today().year)
        self.assertEqual(len(self.library.books), 7)

    def test_year_out_of_range_rejected(self):
        for year in (999, date.today().year + 1):
            with self.subTest(year=year), self.assertRaises(ValidationError):
                self.library.add_book(NEW_ISBN, "Title", "Author", year)

    def test_zero_copies_rejected(self):
        with self.assertRaises(ValidationError):
            self.library.add_book(NEW_ISBN, "Title", "Author", 2000, 0)

    def test_remove_book_deletes_it(self):
        self.library.remove_book(EMMA)
        self.assertNotIn(EMMA, self.library.books)

    def test_remove_unknown_book_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.library.remove_book(NEW_ISBN)

    def test_remove_book_on_loan_rejected(self):
        self.library.issue_book(PRIDE, "M001", ISSUE_DAY)
        with self.assertRaises(UnavailableError):
            self.library.remove_book(PRIDE)


class TestMembers(unittest.TestCase):
    """FR3 register member."""

    def setUp(self):
        self.library = make_library()

    def test_register_member_normalises_id(self):
        member = self.library.register_member(" m004 ", "Dana Demo")
        self.assertEqual(member.member_id, "M004")

    def test_duplicate_member_id_rejected(self):
        with self.assertRaises(ValidationError):
            self.library.register_member("M001", "Someone Else")

    def test_bad_member_id_format_rejected(self):
        for bad in ("M04", "M0004", "X004", "004", ""):
            with self.subTest(member_id=bad), self.assertRaises(ValidationError):
                self.library.register_member(bad, "Name")

    def test_blank_member_name_rejected(self):
        with self.assertRaises(ValidationError):
            self.library.register_member("M004", "  ")


class TestLoans(unittest.TestCase):
    """FR4 issue book, FR5 return book."""

    def setUp(self):
        self.library = make_library()

    def test_issue_sets_due_date_and_reduces_available(self):
        loan = self.library.issue_book(PRIDE, "M001", ISSUE_DAY)
        self.assertEqual(loan.due_date, DUE_DAY)
        self.assertEqual(self.library.get_book(PRIDE).available_copies, 1)

    def test_issue_when_no_copies_left_rejected(self):
        self.library.issue_book(GREAT, "M001", ISSUE_DAY)
        with self.assertRaises(UnavailableError):
            self.library.issue_book(GREAT, "M002", ISSUE_DAY)

    def test_issue_beyond_three_loan_limit_rejected(self):
        for isbn in (PRIDE, GREAT, FRANK):
            self.library.issue_book(isbn, "M001", ISSUE_DAY)
        self.assertEqual(len(self.library.active_loans("M001")), MAX_LOANS_PER_MEMBER)
        with self.assertRaises(UnavailableError):
            self.library.issue_book(JANE, "M001", ISSUE_DAY)

    def test_issue_same_book_twice_to_member_rejected(self):
        self.library.issue_book(PRIDE, "M001", ISSUE_DAY)
        with self.assertRaises(UnavailableError):
            self.library.issue_book(PRIDE, "M001", ISSUE_DAY)

    def test_issue_unknown_book_or_member_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.library.issue_book(NEW_ISBN, "M001", ISSUE_DAY)
        with self.assertRaises(NotFoundError):
            self.library.issue_book(PRIDE, "M999", ISSUE_DAY)

    def test_return_restores_copy_and_records_date(self):
        loan = self.library.issue_book(GREAT, "M001", ISSUE_DAY)
        self.library.return_book(GREAT, "M001", DUE_DAY)
        self.assertEqual(loan.return_date, DUE_DAY)
        self.assertEqual(self.library.get_book(GREAT).available_copies, 1)
        self.assertEqual(self.library.active_loans(), [])

    def test_return_without_active_loan_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            self.library.return_book(PRIDE, "M001", ISSUE_DAY)


class TestFines(unittest.TestCase):
    """FR5 fine calculation: £0.20 per day late, never negative."""

    def setUp(self):
        self.library = make_library()
        self.loan = self.library.issue_book(PRIDE, "M001", ISSUE_DAY)

    def test_fine_is_zero_on_due_date(self):
        self.assertEqual(Library.calculate_fine(self.loan, DUE_DAY), 0.0)

    def test_fine_is_zero_when_early(self):
        self.assertEqual(Library.calculate_fine(self.loan, ISSUE_DAY), 0.0)

    def test_fine_is_20p_one_day_late(self):
        self.assertEqual(Library.calculate_fine(self.loan, DUE_DAY + timedelta(days=1)), 0.20)

    def test_fine_ten_days_late_rounded_to_2dp(self):
        fine = Library.calculate_fine(self.loan, DUE_DAY + timedelta(days=10))
        self.assertEqual(fine, round(10 * FINE_PER_DAY, 2))
        self.assertEqual(fine, 2.0)

    def test_return_book_returns_fine_for_late_return(self):
        fine = self.library.return_book(PRIDE, "M001", DUE_DAY + timedelta(days=3))
        self.assertEqual(fine, 0.60)

    def test_fine_after_return_uses_return_date_not_today(self):
        self.library.return_book(PRIDE, "M001", DUE_DAY + timedelta(days=2))
        much_later = DUE_DAY + timedelta(days=100)
        self.assertEqual(Library.calculate_fine(self.loan, much_later), 0.40)


class TestReservations(unittest.TestCase):
    """FR6 FIFO reservation queue."""

    def setUp(self):
        self.library = make_library()
        self.library.issue_book(GREAT, "M001", ISSUE_DAY)  # only copy now on loan

    def test_reserve_returns_fifo_positions(self):
        self.assertEqual(self.library.reserve_book(GREAT, "M002"), 1)
        self.assertEqual(self.library.reserve_book(GREAT, "M003"), 2)
        self.assertEqual(self.library.reservation_queue(GREAT), ["M002", "M003"])
        self.assertEqual(self.library.next_in_queue(GREAT), "M002")

    def test_reserve_available_book_rejected(self):
        with self.assertRaises(UnavailableError):
            self.library.reserve_book(PRIDE, "M002")

    def test_duplicate_reservation_rejected(self):
        self.library.reserve_book(GREAT, "M002")
        with self.assertRaises(ValidationError):
            self.library.reserve_book(GREAT, "M002")

    def test_member_holding_book_cannot_reserve_it(self):
        with self.assertRaises(UnavailableError):
            self.library.reserve_book(GREAT, "M001")

    def test_only_front_of_queue_may_borrow_returned_book(self):
        self.library.reserve_book(GREAT, "M002")
        self.library.reserve_book(GREAT, "M003")
        self.library.return_book(GREAT, "M001", DUE_DAY)
        with self.assertRaises(UnavailableError):
            self.library.issue_book(GREAT, "M003", DUE_DAY)
        self.library.issue_book(GREAT, "M002", DUE_DAY)
        self.assertEqual(self.library.reservation_queue(GREAT), ["M003"])

    def test_queue_served_in_fifo_order(self):
        self.library.reserve_book(GREAT, "M002")
        self.library.reserve_book(GREAT, "M003")
        self.library.return_book(GREAT, "M001", DUE_DAY)
        self.library.issue_book(GREAT, "M002", DUE_DAY)
        self.library.return_book(GREAT, "M002", DUE_DAY)
        self.library.issue_book(GREAT, "M003", DUE_DAY)
        self.assertIsNone(self.library.next_in_queue(GREAT))
        self.assertNotIn(GREAT, self.library.reservations)

    def test_remove_book_clears_its_queue(self):
        self.library.reserve_book(GREAT, "M002")
        self.library.return_book(GREAT, "M001", DUE_DAY)
        self.library.remove_book(GREAT)
        self.assertNotIn(GREAT, self.library.reservations)
