"""
Library Loans Manager — text-based (command-line) version.

Run:  python cli_app.py

STATUS: starter — menu skeleton only. Each option is wired up in the
`feature/cli` branch once core/library.py is implemented.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

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
    line = "  " + " | ".join(header.ljust(width) for header, width in zip(headers, widths))
    print(line)
    print("  " + "-+-".join("-" * width for width in widths))
    for row in cells:
        print("  " + " | ".join(value.ljust(width) for value, width in zip(row, widths)))


def print_menu() -> None:
    print("\n=== Library Loans Manager ===")
    for key, label in MENU.items():
        print(f"  {key}. {label}")


def main() -> None:
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        if choice in MENU:
            print(f"[{MENU[choice]}] — coming soon (feature/cli).")
        else:
            print("Invalid choice, please enter a number from the menu.")


if __name__ == "__main__":
    main()
