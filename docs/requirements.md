# Requirements — Library Loans Manager

These requirements are shared by **both** versions (text-based and GUI).
IDs are referenced in code comments, tests, the demo video and the report.

## Functional requirements

| ID   | Requirement | Priority (MoSCoW) |
|------|-------------|-------------------|
| FR1  | Add a book with ISBN, title, author, year and number of copies; reject duplicates and invalid ISBNs | Must |
| FR2  | Remove a book, but not while copies are on loan | Must |
| FR3  | Register a member with a unique member ID and name | Must |
| FR4  | Issue a book to a member if a copy is available and the member has fewer than 3 active loans; due date = issue date + 14 days | Must |
| FR5  | Return a book and calculate any overdue fine (£0.20 per day) | Must |
| FR6  | Reserve an unavailable book; reservations are served first-come, first-served (FIFO queue) | Should |
| FR7  | Search books by title, author (partial, case-insensitive) or exact ISBN | Must |
| FR8  | List books sorted by title, author or year, ascending or descending | Must |
| FR9  | Show all overdue loans with days overdue and fine owed | Should |
| FR10 | Save all data to a JSON file and load it on start-up | Must |

## Non-functional requirements

| ID   | Requirement |
|------|-------------|
| NFR1 | Usability — clear menus/labels; every action gives a confirmation or error message |
| NFR2 | Robustness — invalid input never crashes the program |
| NFR3 | Maintainability — all logic in `core/`, shared by both front ends; PEP 8 style, docstrings |
| NFR4 | Portability — runs on Windows, macOS and Linux with standard-library Python 3.10+ only |
| NFR5 | Performance — lookups by ISBN/member ID in O(1); sorting in O(n log n) |
| NFR6 | Data safety — saving writes to a temporary file first so a crash cannot corrupt the data file |
