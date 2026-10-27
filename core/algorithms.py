"""
Hand-written algorithms for the Library Loans Manager (LO1).

These are implemented by hand (not with sorted()/bisect) so the design and
complexity can be discussed in the report.

    merge_sort     O(n log n) time, O(n) space, stable
    binary_search  O(log n) time, requires a list sorted by the same key

STATUS: starter stubs — implemented in the `feature/core` branch.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")


def merge_sort(items: List[T], key: Callable[[T], object], reverse: bool = False) -> List[T]:
    """Return a NEW list of items sorted by key (stable merge sort).

    The input list is not modified.
    """
    # TODO (feature/core): split, recursively sort halves, merge.
    raise NotImplementedError("merge_sort will be implemented in feature/core")


def binary_search(sorted_items: List[T], target: object, key: Callable[[T], object]) -> Optional[T]:
    """Return the item whose key equals target, or None if not found.

    sorted_items must already be sorted ascending by the same key.
    """
    # TODO (feature/core): classic low/high/mid loop.
    raise NotImplementedError("binary_search will be implemented in feature/core")
