"""
Hand-written algorithms for the Library Loans Manager (LO1).

These are implemented by hand (not with sorted()/bisect) so the design and
complexity can be discussed in the report.

    merge_sort     O(n log n) time, O(n) space, stable
    binary_search  O(log n) time, requires a list sorted by the same key

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from typing import Any, Callable, List, Optional, TypeVar

T = TypeVar("T")


def merge_sort(items: List[T], key: Callable[[T], Any], reverse: bool = False) -> List[T]:
    """Return a NEW list of items sorted by key (stable merge sort, FR8, NFR5).

    The input list is not modified. Items with equal keys keep their original
    relative order, also when ``reverse=True`` (the comparison is flipped
    rather than the result reversed, so stability is preserved).

    Complexity: O(n log n) time, O(n) extra space.

    Args:
        items: The list to sort.
        key: Function mapping an item to the value it is compared by.
        reverse: Sort descending instead of ascending.

    Returns:
        A new sorted list.
    """
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], key, reverse)
    right = merge_sort(items[middle:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left: List[T], right: List[T], key: Callable[[T], Any], reverse: bool) -> List[T]:
    """Merge two sorted lists into one, taking from ``left`` on ties (stability)."""
    merged: List[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        left_key, right_key = key(left[i]), key(right[j])
        # Take from the right only when it is strictly "before" the left item,
        # so equal keys always come from the left half first.
        right_first = left_key < right_key if reverse else right_key < left_key
        if right_first:
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search(sorted_items: List[T], target: Any, key: Callable[[T], Any]) -> Optional[T]:
    """Return the item whose key equals target, or None if not found (LO1).

    sorted_items must already be sorted ascending by the same key.

    Complexity: O(log n) time, O(1) extra space (iterative).

    Args:
        sorted_items: List sorted ascending by ``key``.
        target: The key value to look for.
        key: Function mapping an item to its key.

    Returns:
        A matching item, or None.
    """
    low, high = 0, len(sorted_items) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_key = key(sorted_items[mid])
        if mid_key == target:
            return sorted_items[mid]
        if mid_key < target:
            low = mid + 1
        else:
            high = mid - 1
    return None
