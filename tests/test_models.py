"""
Unit tests for core/models.py.

Run all tests:  python -m unittest discover -s tests -v

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

import json
import unittest
from datetime import date
from pathlib import Path

from core.models import Book, Loan, Member

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"


class TestModels(unittest.TestCase):
    def test_book_round_trip(self):
        book = Book("9780141439518", "Pride and Prejudice", "Jane Austen", 1813, 2, 2)
        self.assertEqual(Book.from_dict(book.to_dict()), book)

    def test_member_round_trip(self):
        member = Member("M001", "Alice Example")
        self.assertEqual(Member.from_dict(member.to_dict()), member)

    def test_loan_round_trip_keeps_dates(self):
        loan = Loan("9780141439518", "M001", date(2026, 10, 1), date(2026, 10, 15))
        restored = Loan.from_dict(loan.to_dict())
        self.assertEqual(restored, loan)
        self.assertFalse(restored.is_returned)

    def test_sample_data_loads_into_models(self):
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        books = [Book.from_dict(b) for b in data["books"]]
        members = [Member.from_dict(m) for m in data["members"]]
        self.assertGreater(len(books), 0)
        self.assertGreater(len(members), 0)


if __name__ == "__main__":
    unittest.main()
