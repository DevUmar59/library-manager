# Tests

Run every test from the project root:

```bash
python -m unittest discover -s tests -v
```

The suite uses only `unittest` from the standard library. Date-based tests
pass fixed dates (never the real "today"), and file tests run in a
`tempfile` folder, so results are repeatable and the real data file is never
touched.

## Test classes and the requirements they cover

| File | Test class | Tests | What it checks | Requirements |
|------|------------|------:|----------------|--------------|
| `test_algorithms.py` | `TestMergeSort` | 8 | Ascending/descending, empty and one-item lists, input not mutated, stability (also when reversed), matches `sorted()` on random data | FR8, NFR5, LO1 |
| `test_algorithms.py` | `TestBinarySearch` | 4 | Found (first/middle/last), not found, empty list, key function | NFR5, LO1 |
| `test_library.py` | `TestIsbnValidation` | 3 | Hyphens ignored, bad checksum, wrong length or letters | FR1, NFR2 |
| `test_library.py` | `TestBooks` | 9 | Add book, duplicate ISBN, blank title/author, year bounds (1000 and current year), zero copies, remove, remove unknown, remove while on loan | FR1, FR2 |
| `test_library.py` | `TestMembers` | 4 | Register (ID normalised), duplicate ID, bad ID format, blank name | FR3 |
| `test_library.py` | `TestLoans` | 7 | Due date = issue + 14 days, no copies left, 3-loan limit, same book twice, unknown book/member, return restores copy, return without loan | FR4, FR5 |
| `test_library.py` | `TestFines` | 6 | £0 on due date and when early, £0.20 one day late, rounding, fine from `return_book`, fine fixed once returned | FR5 |
| `test_library.py` | `TestReservations` | 7 | FIFO positions, reserve available book, duplicate reservation, holder cannot reserve, front-of-queue rule, FIFO service order, queue cleared on removal | FR6 |
| `test_library.py` | `TestSearchAndSort` | 11 | Partial case-insensitive title/author search, exact ISBN search, no match, bad field/blank query, sort by title/year/author, stable ties, bad sort field, exact-title binary search | FR7, FR8, LO1 |
| `test_library.py` | `TestOverdue` | 3 | Sorted by due date, due today is not overdue, returned loans excluded | FR9 |
| `test_library.py` | `TestDictRoundTrip` | 1 | `to_dict`/`from_dict` keep books, members, loans and queues | FR10 |
| `test_models.py` | `TestModels` | 4 | Model `to_dict`/`from_dict` round trips, sample data loads | FR10 |
| `test_storage.py` | `TestStorage` | 6 | Missing file gives empty data, save/load round trip, parent folder created and no `.tmp` left, corrupt JSON, missing section, wrong section type | FR10, NFR2, NFR6 |
| `test_storage.py` | `TestLibraryPersistence` | 3 | Sample data used on first run, save/load keeps loans and queues, invalid record rejected | FR10, NFR2 |

**Total: 76 tests.**

NFR3 (all logic in `core/`) is supported by the fact that every test above
exercises `core/` directly, with no user interface involved.
