"""
Unit tests for core/algorithms.py (merge_sort, binary_search — LO1, FR8, NFR5).

Run all tests:  python -m unittest discover -s tests -v

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

import random
import unittest

from core.algorithms import binary_search, merge_sort


def identity(value):
    return value


def first(pair):
    return pair[0]


class TestMergeSort(unittest.TestCase):
    """merge_sort: normal, boundary and stability cases."""

    def test_sorts_numbers_ascending(self):
        self.assertEqual(merge_sort([5, 2, 9, 1, 5, 6], key=identity), [1, 2, 5, 5, 6, 9])

    def test_sorts_descending_with_reverse(self):
        self.assertEqual(merge_sort([3, 1, 2], key=identity, reverse=True), [3, 2, 1])

    def test_empty_list_returns_empty_list(self):
        self.assertEqual(merge_sort([], key=identity), [])

    def test_single_item_list(self):
        self.assertEqual(merge_sort([42], key=identity), [42])

    def test_does_not_mutate_input_and_returns_new_list(self):
        data = [3, 1, 2]
        result = merge_sort(data, key=identity)
        self.assertEqual(data, [3, 1, 2])
        self.assertIsNot(result, data)

    def test_stable_for_duplicate_keys(self):
        data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
        self.assertEqual(merge_sort(data, key=first), [(1, "b"), (1, "d"), (2, "a"), (2, "c")])

    def test_reverse_is_still_stable(self):
        data = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
        self.assertEqual(
            merge_sort(data, key=first, reverse=True), [(2, "a"), (2, "c"), (1, "b"), (1, "d")]
        )

    def test_matches_builtin_sorted_on_random_data(self):
        rng = random.Random(1234)  # fixed seed: repeatable test
        data = [rng.randint(-50, 50) for _ in range(200)]
        self.assertEqual(merge_sort(data, key=identity), sorted(data))


class TestBinarySearch(unittest.TestCase):
    """binary_search: found, not found and empty cases."""

    def setUp(self):
        self.items = list(range(0, 100, 5))  # 0, 5, ..., 95

    def test_finds_middle_first_and_last_items(self):
        for target in (0, 50, 95):
            self.assertEqual(binary_search(self.items, target, key=identity), target)

    def test_returns_none_when_not_found(self):
        self.assertIsNone(binary_search(self.items, 7, key=identity))
        self.assertIsNone(binary_search(self.items, 100, key=identity))
        self.assertIsNone(binary_search(self.items, -5, key=identity))

    def test_returns_none_on_empty_list(self):
        self.assertIsNone(binary_search([], 1, key=identity))

    def test_uses_key_function(self):
        words = merge_sort(["pear", "Apple", "banana"], key=str.lower)
        self.assertEqual(binary_search(words, "apple", key=str.lower), "Apple")


if __name__ == "__main__":
    unittest.main()
