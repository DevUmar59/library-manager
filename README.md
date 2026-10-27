# Library Loans Manager

A Python application for a small library to manage books, members, loans,
reservations and overdue fines. It is built **twice over one shared core**:

- **Text-based version** — `cli_app.py` (menu-driven, command line)
- **GUI version** — `gui_app.py` (Tkinter)

Both versions use the same `core/` package for data handling, algorithms and
file storage, so they have identical functionality.

> **Status:** starter skeleton. See [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md)
> for the development plan and [docs/requirements.md](docs/requirements.md) for
> the requirements (FR1–FR10, NFR1–NFR6).

## Features (target)

- Add / remove books, register members
- Issue and return books, with 14-day loans and £0.20/day overdue fines
- First-come, first-served reservation queue for unavailable books
- Search by title, author or ISBN; sort by title, author or year
- Overdue report
- Data saved to JSON between runs

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

## Running the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```
library-manager/
├── core/               shared logic (no input/print here)
│   ├── models.py       Book, Member, Loan dataclasses
│   ├── library.py      Library class — business rules
│   ├── algorithms.py   merge sort, binary search
│   ├── storage.py      JSON load/save
│   └── exceptions.py   custom error types
├── cli_app.py          text-based front end
├── gui_app.py          Tkinter front end
├── tests/              unittest test cases
├── data/               sample_data.json (fictional data only)
├── docs/               requirements and Git workflow
├── submission/         (git-ignored) video + report for Assessment 1
└── finalize.py         builds the Assessment 1 ZIP
```

## GenAI statement

Generative AI (Claude, Anthropic) was used to help draft this README, the
`.gitignore`, project scaffolding and code. Every code file carries a GenAI
declaration at the top. All output was reviewed, tested and modified by the
author. *(Edit this paragraph so it accurately describes your own use.)*

## Author

[Your Name] — CSC-44102, Keele University
