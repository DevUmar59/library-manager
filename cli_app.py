"""
Library Loans Manager — text-based (command-line) version.

Run:  python cli_app.py

STATUS: starter — menu skeleton only. Each option is wired up in the
`feature/cli` branch once core/library.py is implemented.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Sequence

from core.exceptions import LibraryError
from core.library import Library, validate_isbn
from core.models import Book
from core.storage import DEFAULT_DATA_FILE

# Each action takes the Library and returns True if it changed the data.
Action = Callable[[Library], bool]

MENU = {
    "1": "Add a book",
    "2": "Remove a book",
    "3": "Register a member",
    "4": "Issue a book",
    "5": "Return a book",
    "6": "Reserve a book",
    "7": "Search books",
    "8": "List books (sorted)",
    "9": "Show overdue loans and fines",
    "0": "Save and exit",
}


# ---- Input helpers (NFR2: re-prompt on bad input, never crash) -------------
def ask_text(prompt: str, allow_empty: bool = False) -> str:
    """Ask for a line of text, re-prompting until it is non-empty (unless allowed)."""
    while True:
        value = input(f"{prompt}: ").strip()
        if value or allow_empty:
            return value
        print("  Please enter a value.")


def ask_int(prompt: str, min_value: int, max_value: int) -> int:
    """Ask for a whole number in ``min_value..max_value``, re-prompting on bad input."""
    while True:
        raw = input(f"{prompt} ({min_value}-{max_value}): ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if min_value <= value <= max_value:
            return value
        print(f"  Please enter a number from {min_value} to {max_value}.")


def ask_choice(prompt: str, choices: Dict[str, str]) -> str:
    """Show numbered ``choices`` (key -> label) and return the chosen key."""
    while True:
        print(prompt)
        for key, label in choices.items():
            print(f"  {key}. {label}")
        value = input("Choose: ").strip().lower()
        if value in choices:
            return value
        print(f"  Please choose one of: {', '.join(choices)}.")


def ask_yes_no(prompt: str) -> bool:
    """Ask a yes/no question; return True for yes."""
    while True:
        value = input(f"{prompt} (y/n): ").strip().lower()
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("  Please answer y or n.")


# ---- Output helpers (NFR1: clear, aligned output) --------------------------
def print_table(headers: Sequence[str], rows: List[Sequence[object]]) -> None:
    """Print rows as an aligned text table with a header line."""
    if not rows:
        print("  (nothing to show)")
        return
    cells = [[str(value) for value in row] for row in rows]
    widths = [max(len(headers[i]), *(len(row[i]) for row in cells)) for i in range(len(headers))]
    print("  " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)).rstrip())
    print("  " + "-+-".join("-" * w for w in widths))
    for row in cells:
        print("  " + " | ".join(v.ljust(w) for v, w in zip(row, widths)).rstrip())


def print_books(books: List[Book]) -> None:
    """Print books as a table: ISBN | Title | Author | Year | Available."""
    print_table(
        ("ISBN", "Title", "Author", "Year", "Available"),
        [(b.isbn, b.title, b.author, b.year, f"{b.available_copies}/{b.total_copies}") for b in books],
    )


# ---- Menu actions: one small function per option ---------------------------
def add_book(library: Library) -> bool:
    """Menu 1 — add a book (FR1)."""
    isbn = validate_isbn(ask_text("ISBN-13"))  # fail fast before asking the rest
    title = ask_text("Title")
    author = ask_text("Author")
    year = ask_int("Year published", 1000, date.today().year)
    copies = ask_int("Number of copies", 1, 999)
    book = library.add_book(isbn, title, author, year, copies)
    print(f"Added '{book.title}' ({book.isbn}) with {book.total_copies} cop{'y' if book.total_copies == 1 else 'ies'}.")
    return True


def remove_book(library: Library) -> bool:
    """Menu 2 — remove a book that has no copies on loan (FR2)."""
    book = library.get_book(ask_text("ISBN of the book to remove"))
    if not ask_yes_no(f"Remove '{book.title}' by {book.author}?"):
        print("Cancelled.")
        return False
    library.remove_book(book.isbn)
    print(f"Removed '{book.title}'.")
    return True


def register_member(library: Library) -> bool:
    """Menu 3 — register a new member (FR3)."""
    member_id = ask_text("Member ID (e.g. M004)")
    name = ask_text("Name")
    member = library.register_member(member_id, name)
    print(f"Registered {member.name} as {member.member_id}.")
    return True


# Dispatch table: menu key -> action function (no long if/elif chain).
ACTIONS: Dict[str, Action] = {
    "1": add_book,
    "2": remove_book,
    "3": register_member,
}


def print_menu() -> None:
    """Print the main menu."""
    print("\n=== Library Loans Manager ===")
    for key, label in MENU.items():
        print(f"  {key}. {label}")


def save(library: Library, path: Path) -> None:
    """Save the library, reporting (not raising) any error (FR10, NFR2)."""
    try:
        library.save(path)
    except LibraryError as exc:
        print(f"Warning: could not save data: {exc}")


def run_action(library: Library, choice: str, path: Path) -> None:
    """Run one menu action, show any library error, and save after a change."""
    action = ACTIONS.get(choice)
    if action is None:
        print(f"[{MENU[choice]}] - not available yet.")
        return
    try:
        if action(library):
            save(library, path)
    except LibraryError as exc:
        print(f"Error: {exc}")


def main(path: Path = DEFAULT_DATA_FILE) -> int:
    """Run the text menu until the user saves and exits. Returns an exit code."""
    # Never crash on a console that cannot show a character such as '£' (NFR2, NFR4).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        library = Library.load(path)
    except LibraryError as exc:
        print(f"Could not load data: {exc}")
        print(f"Fix or delete {path} and try again.")
        return 1
    print(f"Loaded {len(library.books)} books and {len(library.members)} members.")

    try:
        while True:
            print_menu()
            choice = input("Choose an option: ").strip()
            if choice == "0":
                break
            if choice in MENU:
                run_action(library, choice, path)
            else:
                print("Invalid choice, please enter a number from the menu.")
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted.")
    save(library, path)
    print("Data saved. Goodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
