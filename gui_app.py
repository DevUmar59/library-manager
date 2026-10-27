"""
Library Loans Manager — GUI version (Tkinter, standard library).

Run:  python gui_app.py

A second front end over the same core.library.Library used by cli_app.py:
every button calls one Library method, and no business rules live here
(NFR3). Each tab is a ttk.Frame subclass inside a ttk.Notebook; after any
change the app calls refresh_all() so every tab shows the same data.

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, Type

from core.exceptions import LibraryError
from core.library import Library
from core.storage import DEFAULT_DATA_FILE

APP_TITLE = "Library Loans Manager"

# (column id, heading text, width in pixels)
Column = Tuple[str, str, int]


class BaseTab(ttk.Frame):
    """Shared helpers for every tab: access to the app, tables and form rows."""

    title = "Tab"

    def __init__(self, parent: ttk.Notebook, app: "LibraryApp") -> None:
        super().__init__(parent, padding=10)
        self.app = app

    @property
    def library(self) -> Library:
        """The Library shared by all tabs (replaced on File > Reload)."""
        return self.app.library

    def refresh(self) -> None:
        """Redraw the tab from the current library data."""

    @staticmethod
    def make_table(
        parent: tk.Misc, columns: Sequence[Column], show: str = "headings"
    ) -> Tuple[ttk.Frame, ttk.Treeview]:
        """Return (frame, tree): a Treeview with a vertical scrollbar in a frame."""
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show=show, selectmode="browse")
        for col_id, heading, width in columns:
            tree.heading(col_id, text=heading, anchor="w")
            tree.column(col_id, width=width, minwidth=40, anchor="w", stretch=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return frame, tree

    @staticmethod
    def fill_table(tree: ttk.Treeview, rows: Iterable[Tuple[str, Sequence[object]]]) -> None:
        """Replace the rows of ``tree`` with (row id, values) pairs."""
        tree.delete(*tree.get_children())
        for row_id, values in rows:
            tree.insert("", "end", iid=row_id, values=list(values))

    @staticmethod
    def add_field(form: tk.Misc, row: int, label: str, widget: tk.Widget) -> None:
        """Place a label and an input widget on one row of a grid form."""
        ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 6), pady=2)
        widget.grid(row=row, column=1, sticky="ew", pady=2)


def first_token(text: str) -> str:
    """Return the ID part of a combobox entry such as 'M001 - Alice Example'."""
    parts = text.split()
    return parts[0] if parts else ""


class LibraryApp(tk.Tk):
    """Main window: menu bar, one tab per feature area and a status bar."""

    def __init__(self, library: Library, data_path: Path = DEFAULT_DATA_FILE) -> None:
        super().__init__()
        self.library = library
        self.data_path = Path(data_path)
        self.dirty = False  # True when there are unsaved changes
        self.title(APP_TITLE)
        self.geometry("900x560")
        self.minsize(760, 480)

        self._build_menu()
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        self.status = tk.StringVar(
            value=f"Loaded {len(library.books)} books and {len(library.members)} members."
        )
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w", padding=(6, 2)).grid(
            row=1, column=0, sticky="ew"
        )
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tabs: List[BaseTab] = []
        for tab_class in TAB_CLASSES:
            tab = tab_class(self.notebook, self)
            self.notebook.add(tab, text=tab.title)
            self.tabs.append(tab)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)  # save on close
        self.bind_all("<Control-s>", lambda _event: self.save())
        self.refresh_all()

    def _build_menu(self) -> None:
        """Create the File menu: Save, Reload, Exit."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
        file_menu.add_command(label="Reload", command=self.reload)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    # ---- Shared actions ---------------------------------------------------
    def set_status(self, message: str) -> None:
        """Show ``message`` in the status bar (NFR1)."""
        self.status.set(message)

    def _set_dirty(self, dirty: bool) -> None:
        self.dirty = dirty
        self.title(f"{APP_TITLE}{' - unsaved changes' if dirty else ''}")

    def refresh_all(self) -> None:
        """Redraw every tab so they all show the same data."""
        for tab in self.tabs:
            tab.refresh()

    def perform(self, action: Callable[[], Optional[str]]) -> bool:
        """Run a Library action that changes data.

        On success the data is marked unsaved, every tab is refreshed and the
        returned message is shown in the status bar. A LibraryError is shown
        in an error box instead of crashing (NFR1, NFR2). Returns True on
        success.
        """
        try:
            message = action()
        except LibraryError as exc:
            self.set_status(f"Error: {exc}")
            messagebox.showerror("Cannot do that", str(exc), parent=self)
            return False
        self._set_dirty(True)
        self.refresh_all()
        if message:
            self.set_status(message)
        return True

    def save(self) -> bool:
        """File > Save: write all data to the JSON file (FR10, NFR6)."""
        try:
            self.library.save(self.data_path)
        except LibraryError as exc:
            messagebox.showerror("Save failed", str(exc), parent=self)
            return False
        self._set_dirty(False)
        self.set_status(f"Saved to {self.data_path.name} at {datetime.now():%H:%M:%S}.")
        return True

    def reload(self) -> None:
        """File > Reload: discard unsaved changes and load the data file again."""
        if self.dirty and not messagebox.askyesno(
            "Reload", "Discard unsaved changes and reload from the data file?", parent=self
        ):
            return
        try:
            self.library = Library.load(self.data_path)
        except LibraryError as exc:
            messagebox.showerror("Reload failed", str(exc), parent=self)
            return
        self._set_dirty(False)
        self.refresh_all()
        self.set_status(f"Reloaded {len(self.library.books)} books from {self.data_path.name}.")

    def on_exit(self) -> None:
        """File > Exit and window close: offer to save unsaved changes first."""
        if self.dirty:
            answer = messagebox.askyesnocancel("Exit", "Save changes before exiting?", parent=self)
            if answer is None:
                return
            if answer and not self.save():
                return
        self.destroy()


# Tabs shown in the notebook, in order.
TAB_CLASSES: List[Type[BaseTab]] = []


def main(data_path: Path = DEFAULT_DATA_FILE) -> None:
    """Load the data and start the GUI; show a message if the file is corrupt."""
    try:
        library = Library.load(data_path)
    except LibraryError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            APP_TITLE, f"Could not load data:\n{exc}\n\nFix or delete {data_path} and try again."
        )
        root.destroy()
        return
    LibraryApp(library, data_path).mainloop()


if __name__ == "__main__":
    main()
