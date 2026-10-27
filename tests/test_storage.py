"""
Unit tests for core/storage.py and Library.load/save (FR10, NFR6).

Every test works inside a temporary folder, so the real data file is never
touched.

Run all tests:  python -m unittest discover -s tests -v

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from core.exceptions import LibraryError
from core.library import Library
from core.storage import SAMPLE_DATA_FILE, load_data, save_data

GREAT = "9780141439570"


class TestStorage(unittest.TestCase):
    """load_data / save_data."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self._tmp.name)
        self.path = self.folder / "library_data.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_file_returns_empty_structure(self):
        self.assertEqual(
            load_data(self.path), {"books": [], "members": [], "loans": [], "reservations": {}}
        )

    def test_save_then_load_returns_same_data(self):
        data = {"books": [], "members": [{"member_id": "M001", "name": "Alice"}],
                "loans": [], "reservations": {}}
        save_data(data, self.path)
        self.assertEqual(load_data(self.path), data)

    def test_save_creates_parent_folder_and_leaves_no_temp_file(self):
        nested = self.folder / "new" / "data.json"
        save_data({"books": [], "members": [], "loans": [], "reservations": {}}, nested)
        self.assertTrue(nested.exists())
        self.assertFalse(nested.with_suffix(".tmp").exists())

    def test_corrupt_json_raises_library_error(self):
        self.path.write_text("{ not valid json", encoding="utf-8")
        with self.assertRaises(LibraryError):
            load_data(self.path)

    def test_missing_section_raises_library_error(self):
        self.path.write_text(json.dumps({"books": [], "members": []}), encoding="utf-8")
        with self.assertRaises(LibraryError):
            load_data(self.path)

    def test_wrong_section_type_raises_library_error(self):
        self.path.write_text(
            json.dumps({"books": {}, "members": [], "loans": [], "reservations": {}}),
            encoding="utf-8",
        )
        with self.assertRaises(LibraryError):
            load_data(self.path)


class TestLibraryPersistence(unittest.TestCase):
    """Library.save / Library.load."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "library_data.json"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_without_data_file_uses_sample_data(self):
        library = Library.load(self.path)
        sample = json.loads(SAMPLE_DATA_FILE.read_text(encoding="utf-8"))
        self.assertEqual(len(library.books), len(sample["books"]))
        self.assertEqual(len(library.members), len(sample["members"]))

    def test_save_load_round_trip_keeps_loans_and_queue(self):
        library = Library.load(self.path)
        library.issue_book(GREAT, "M001", date(2026, 3, 1))
        library.reserve_book(GREAT, "M002")
        library.save(self.path)
        restored = Library.load(self.path)
        self.assertEqual(restored.to_dict(), library.to_dict())
        self.assertEqual(restored.active_loans("M001")[0].due_date, date(2026, 3, 15))
        self.assertEqual(restored.next_in_queue(GREAT), "M002")

    def test_invalid_record_raises_library_error(self):
        self.path.write_text(
            json.dumps({"books": [{"isbn": GREAT}], "members": [], "loans": [], "reservations": {}}),
            encoding="utf-8",
        )
        with self.assertRaises(LibraryError):
            Library.load(self.path)


if __name__ == "__main__":
    unittest.main()
