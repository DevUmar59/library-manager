# Library Loans Manager

A Python application for a small library to manage books, members, loans,
reservations and overdue fines. It is built **twice over one shared core**:

- **Text-based version** — `cli_app.py` (menu-driven, command line)
- **GUI version** — `gui_app.py` (Tkinter)

Both versions use the same `core/` package for data handling, algorithms and
file storage, so they have identical functionality. The requirements are
listed in [docs/requirements.md](docs/requirements.md) (FR1–FR10, NFR1–NFR6)
and the design in [docs/design.md](docs/design.md).

## Features

| Feature | Requirement |
|---------|-------------|
| Add books (ISBN-13 checksum validation, duplicates rejected) and remove books (not while on loan) | FR1, FR2 |
| Register members with IDs such as `M004` | FR3 |
| Issue books: 14-day loans, maximum 3 active loans per member | FR4 |
| Return books with an overdue fine of £0.20 per day | FR5 |
| Reserve unavailable books in a first-come, first-served (FIFO) queue; only the member at the front can borrow the returned copy | FR6 |
| Search by title or author (partial, case-insensitive) or exact ISBN | FR7 |
| List books sorted by title, author or year, ascending or descending (hand-written merge sort) | FR8 |
| Overdue report with days overdue, fines and total | FR9 |
| Data saved to JSON with a crash-safe write, loaded on start-up | FR10, NFR6 |

## Requirements

- Python **3.10+**
- No third-party packages (Tkinter ships with Python).
  Check Tkinter works with `python -m tkinter` — a small test window should open.
  On some Linux systems: `sudo apt install python3-tk`

## How to run

```bash
git clone https://github.com/<your-username>/library-manager.git
cd library-manager

python cli_app.py     # text-based version
python gui_app.py     # GUI version
```

Use `python3` instead of `python` on macOS/Linux if needed.

On the first run the app loads the fictional sample data in
`data/sample_data.json`. Your changes are saved to `data/library_data.json`,
which is not tracked by Git. Delete that file to start again from the sample
data.

## How to use

### Text-based version

1. Run `python cli_app.py`. A numbered menu appears.
2. Type the number of an option and press Enter, then answer the prompts.
   Bad input (letters for a year, an unknown menu number, etc.) is rejected and
   you are asked again, so the program never crashes.
3. Lists are shown as aligned tables: `ISBN | Title | Author | Year | Available`.
4. Data is saved after every change. Option **0** saves and exits; Ctrl+C also
   saves before exiting.

| Option | Action |
|--------|--------|
| 1 / 2 | Add a book / remove a book (asks for confirmation) |
| 3 | Register a member |
| 4 / 5 | Issue a book / return a book (shows the fine and who is next in the queue) |
| 6 | Reserve a book that has no copies available |
| 7 | Search: choose title, author or ISBN, then type the search text |
| 8 | List all books: choose the sort field and ascending or descending |
| 9 | Overdue loans: member, title, due date, days overdue, fine and total |

### GUI version

1. Run `python gui_app.py`. The window has five tabs and a status bar that
   shows the result of the last action.
2. **Books** — the table lists every book. Click the **Title**, **Author** or
   **Year** header to sort; click again to reverse. Use the search box (choose
   the field first) and **Show all** to clear it. Add books with the form on the
   right; select a row and press **Remove selected book** to remove one.
3. **Members** — the member table and a form to register new members.
4. **Loans** — choose a book and a member and press **Issue book**. Click a row in
   the active loans table to fill the form, then press **Return book**. Overdue
   loans are shown in red.
5. **Reservations** — reserve a book that has no copies left. The table shows each
   book's queue in order.
6. **Overdue** — overdue loans as of today with fines and the total owed.
7. **File** menu: **Save** (Ctrl+S), **Reload** (discard unsaved changes) and
   **Exit**. If there are unsaved changes, closing the window asks whether to save.

Errors (such as an invalid ISBN or a member with 3 loans) appear in a message
box; nothing is changed when an action fails.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

76 unit tests cover the algorithms, every business rule and the JSON storage.
[tests/README.md](tests/README.md) maps each test class to the requirements it
checks, and [docs/test_results.txt](docs/test_results.txt) has the output of
the latest run.

## Project structure

```
library-manager/
├── core/               shared logic (no input/print/tkinter here)
│   ├── models.py       Book, Member, Loan dataclasses
│   ├── library.py      Library class — business rules
│   ├── algorithms.py   merge sort, binary search
│   ├── storage.py      JSON load/save (safe write)
│   └── exceptions.py   custom error types
├── cli_app.py          text-based front end
├── gui_app.py          Tkinter front end
├── tests/              unittest test cases + README mapping tests to requirements
├── data/               sample_data.json (fictional data only)
├── docs/               requirements, design, test results, Git workflow
├── submission/         (git-ignored) video + report for Assessment 1
└── finalize.py         builds the Assessment 1 ZIP
```

## GenAI statement

Generative AI (Claude, Anthropic) was used to help draft this README, the
`.gitignore`, project scaffolding, the code, the unit tests and the design
documentation. Every code file carries a GenAI declaration at the top. All
output was reviewed, tested and modified by the author. *(Edit this paragraph
so it accurately describes your own use.)*

## Author

[Your Name] — CSC-44102, Keele University
