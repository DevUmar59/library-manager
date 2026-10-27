"""
Library Loans Manager — text-based (command-line) version.

Run:  python cli_app.py

STATUS: starter — menu skeleton only. Each option is wired up in the
`feature/cli` branch once core/library.py is implemented.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

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
