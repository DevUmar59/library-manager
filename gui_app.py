"""
Library Loans Manager — GUI version (Tkinter, standard library).

Run:  python gui_app.py

STATUS: starter — window layout only. Tabs are wired to core/library.py in
the `feature/gui` branch (merged through a pull request).

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

TABS = ("Books", "Members", "Loans", "Reservations", "Overdue")


class LibraryApp(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Library Loans Manager")
        self.geometry("900x560")
        self.minsize(720, 460)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)
        for name in TABS:
            frame = ttk.Frame(notebook, padding=16)
            ttk.Label(frame, text=f"{name} tab — coming soon (feature/gui)").pack(anchor="w")
            notebook.add(frame, text=name)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(
            fill="x", side="bottom"
        )


def main() -> None:
    LibraryApp().mainloop()


if __name__ == "__main__":
    main()
