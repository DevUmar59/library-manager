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
from datetime import date, datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, Type

from core.exceptions import LibraryError, ValidationError
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


def parse_int(text: str, label: str) -> int:
    """Convert form text to int, raising ValidationError with a friendly message."""
    try:
        return int(text.strip())
    except ValueError:
        raise ValidationError(f"{label} must be a whole number.") from None


class BooksTab(BaseTab):
    """Books: sortable table, search box, add-book form and remove (FR1, FR2, FR7, FR8)."""

    title = "Books"
    COLUMNS: Sequence[Column] = (
        ("isbn", "ISBN", 120),
        ("title", "Title", 230),
        ("author", "Author", 150),
        ("year", "Year", 60),
        ("available", "Available", 80),
    )
    SORTABLE = ("title", "author", "year")  # fields Library.sorted_books accepts

    def __init__(self, parent: ttk.Notebook, app: "LibraryApp") -> None:
        super().__init__(parent, app)
        self.sort_field = "title"
        self.sort_reverse = False
        self.active_search: Optional[Tuple[str, str]] = None  # (query, field)

        # Search bar (FR7)
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(bar, text="Search").pack(side="left")
        self.search_field = tk.StringVar(value="title")
        ttk.Combobox(
            bar, textvariable=self.search_field, values=("title", "author", "isbn"),
            state="readonly", width=8,
        ).pack(side="left", padx=4)
        self.search_text = tk.StringVar()
        entry = ttk.Entry(bar, textvariable=self.search_text)
        entry.pack(side="left", padx=4, fill="x", expand=True)
        entry.bind("<Return>", lambda _event: self.search())
        ttk.Button(bar, text="Search", command=self.search).pack(side="left", padx=4)
        ttk.Button(bar, text="Show all", command=self.clear_search).pack(side="left")

        # Table; clicking Title/Author/Year headers sorts with merge sort (FR8)
        table, self.tree = self.make_table(self, self.COLUMNS)
        table.grid(row=1, column=0, sticky="nsew")
        for field in self.SORTABLE:
            self.tree.heading(field, command=lambda f=field: self.sort_by(f))

        # Side panel: add form (FR1) and remove button (FR2)
        side = ttk.Frame(self)
        side.grid(row=1, column=1, sticky="ns", padx=(10, 0))
        form = ttk.LabelFrame(side, text="Add a book", padding=8)
        form.grid(row=0, column=0, sticky="ew")
        self.fields = {name: tk.StringVar() for name in ("isbn", "title", "author", "year")}
        self.copies = tk.StringVar(value="1")
        labels = (("isbn", "ISBN-13"), ("title", "Title"), ("author", "Author"), ("year", "Year"))
        for row, (name, label) in enumerate(labels):
            self.add_field(form, row, label, ttk.Entry(form, textvariable=self.fields[name], width=24))
        self.add_field(form, 4, "Copies", ttk.Spinbox(form, from_=1, to=999, textvariable=self.copies, width=6))
        ttk.Button(form, text="Add book", command=self.add_book).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        remove = ttk.LabelFrame(side, text="Remove", padding=8)
        remove.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(remove, text="Remove selected book", command=self.remove_selected).pack(fill="x")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def refresh(self) -> None:
        """Show books sorted by the current header, filtered by the active search."""
        books = self.library.sorted_books(self.sort_field, self.sort_reverse)
        if self.active_search:
            query, field = self.active_search
            matches = {book.isbn for book in self.library.search_books(query, field)}
            books = [book for book in books if book.isbn in matches]
        self.fill_table(self.tree, (
            (b.isbn, (b.isbn, b.title, b.author, b.year, f"{b.available_copies}/{b.total_copies}"))
            for b in books
        ))
        for field, heading, _width in self.COLUMNS:  # arrow marks the sorted column
            arrow = (" ▼" if self.sort_reverse else " ▲") if field == self.sort_field else ""
            self.tree.heading(field, text=heading + arrow)

    def sort_by(self, field: str) -> None:
        """Header click: sort by ``field``; clicking the same header toggles asc/desc."""
        self.sort_reverse = not self.sort_reverse if field == self.sort_field else False
        self.sort_field = field
        self.refresh()
        order = "descending" if self.sort_reverse else "ascending"
        self.app.set_status(f"Books sorted by {field}, {order}.")

    def search(self) -> None:
        """Run the search in the search box (FR7)."""
        query, field = self.search_text.get(), self.search_field.get()
        try:
            count = len(self.library.search_books(query, field))
        except LibraryError as exc:
            messagebox.showerror("Search", str(exc), parent=self)
            return
        self.active_search = (query, field)
        self.refresh()
        self.app.set_status(f"{count} book(s) found for {field} '{query.strip()}'.")

    def clear_search(self) -> None:
        """Show every book again."""
        self.active_search = None
        self.search_text.set("")
        self.refresh()
        self.app.set_status(f"Showing all {len(self.library.books)} books.")

    def add_book(self) -> None:
        """Add the book in the form (FR1)."""
        values = {name: var.get() for name, var in self.fields.items()}

        def action() -> str:
            year = parse_int(values["year"], "Year")
            copies = parse_int(self.copies.get(), "Copies")
            book = self.library.add_book(values["isbn"], values["title"], values["author"], year, copies)
            return f"Added '{book.title}' ({book.isbn}) with {book.total_copies} copies."

        if self.app.perform(action):
            for var in self.fields.values():
                var.set("")
            self.copies.set("1")

    def remove_selected(self) -> None:
        """Remove the selected book after confirmation (FR2)."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Remove book", "Select a book in the table first.", parent=self)
            return
        book = self.library.books.get(selected[0])
        if book is None or not messagebox.askyesno(
            "Remove book", f"Remove '{book.title}' by {book.author}?", parent=self
        ):
            return

        def action() -> str:
            self.library.remove_book(book.isbn)
            return f"Removed '{book.title}'."

        self.app.perform(action)


class MembersTab(BaseTab):
    """Members: table of members and a registration form (FR3)."""

    title = "Members"
    COLUMNS: Sequence[Column] = (
        ("member_id", "Member ID", 90),
        ("name", "Name", 260),
        ("loans", "Active loans", 100),
    )

    def __init__(self, parent: ttk.Notebook, app: "LibraryApp") -> None:
        super().__init__(parent, app)
        table, self.tree = self.make_table(self, self.COLUMNS)
        table.grid(row=0, column=0, sticky="nsew")

        form = ttk.LabelFrame(self, text="Register a member", padding=8)
        form.grid(row=0, column=1, sticky="n", padx=(10, 0))
        self.member_id = tk.StringVar()
        self.name = tk.StringVar()
        self.add_field(form, 0, "Member ID", ttk.Entry(form, textvariable=self.member_id, width=24))
        ttk.Label(form, text="Format: M + 3 digits, e.g. M004", foreground="gray").grid(
            row=1, column=1, sticky="w"
        )
        self.add_field(form, 2, "Name", ttk.Entry(form, textvariable=self.name, width=24))
        ttk.Button(form, text="Register member", command=self.register).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def refresh(self) -> None:
        """Show every member with their number of active loans."""
        self.fill_table(self.tree, (
            (m.member_id, (m.member_id, m.name, len(self.library.active_loans(m.member_id))))
            for m in self.library.list_members()
        ))

    def register(self) -> None:
        """Register the member in the form (FR3)."""
        member_id, name = self.member_id.get(), self.name.get()

        def action() -> str:
            member = self.library.register_member(member_id, name)
            return f"Registered {member.name} as {member.member_id}."

        if self.app.perform(action):
            self.member_id.set("")
            self.name.set("")


def book_choices(library: Library) -> List[str]:
    """Combobox entries 'ISBN - Title', ordered by title."""
    return [f"{b.isbn} - {b.title}" for b in library.sorted_books("title")]


def member_choices(library: Library) -> List[str]:
    """Combobox entries 'ID - Name', ordered by member ID."""
    return [f"{m.member_id} - {m.name}" for m in library.list_members()]


class LoansTab(BaseTab):
    """Loans: issue and return forms plus a table of active loans (FR4, FR5)."""

    title = "Loans"
    COLUMNS: Sequence[Column] = (
        ("member", "Member", 150),
        ("title", "Title", 210),
        ("isbn", "ISBN", 115),
        ("issued", "Issued", 90),
        ("due", "Due", 90),
        ("status", "Status", 80),
    )

    def __init__(self, parent: ttk.Notebook, app: "LibraryApp") -> None:
        super().__init__(parent, app)
        ttk.Label(self, text="Active loans (click a row to fill the form for a return)").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        table, self.tree = self.make_table(self, self.COLUMNS)
        table.grid(row=1, column=0, sticky="nsew")
        self.tree.tag_configure("overdue", foreground="#b00020")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ttk.LabelFrame(self, text="Issue or return", padding=8)
        form.grid(row=1, column=1, sticky="n", padx=(10, 0))
        self.book = tk.StringVar()
        self.member = tk.StringVar()
        self.book_box = ttk.Combobox(form, textvariable=self.book, width=30)
        self.member_box = ttk.Combobox(form, textvariable=self.member, width=30)
        self.add_field(form, 0, "Book", self.book_box)
        self.add_field(form, 1, "Member", self.member_box)
        ttk.Button(form, text="Issue book", command=self.issue).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Button(form, text="Return book", command=self.return_book).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0)
        )
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def refresh(self) -> None:
        """Show active loans (overdue ones in red) and update the dropdowns."""
        today = date.today()
        self.tree.delete(*self.tree.get_children())
        for loan in self.library.active_loans():
            member = self.library.members.get(loan.member_id)
            book = self.library.books.get(loan.isbn)
            overdue = loan.due_date < today
            self.tree.insert(
                "", "end", iid=f"{loan.isbn}|{loan.member_id}",
                values=(
                    f"{loan.member_id} - {member.name if member else '?'}",
                    book.title if book else "?",
                    loan.isbn,
                    loan.issue_date.isoformat(),
                    loan.due_date.isoformat(),
                    "OVERDUE" if overdue else "On loan",
                ),
                tags=("overdue",) if overdue else (),
            )
        self.book_box["values"] = book_choices(self.library)
        self.member_box["values"] = member_choices(self.library)

    def on_select(self, _event: object = None) -> None:
        """Copy the selected loan's book and member into the form."""
        selected = self.tree.selection()
        if not selected:
            return
        isbn, member_id = selected[0].split("|")
        book = self.library.books.get(isbn)
        member = self.library.members.get(member_id)
        self.book.set(f"{isbn} - {book.title}" if book else isbn)
        self.member.set(f"{member_id} - {member.name}" if member else member_id)

    def issue(self) -> None:
        """Issue the chosen book to the chosen member (FR4)."""
        isbn, member_id = first_token(self.book.get()), first_token(self.member.get())

        def action() -> str:
            loan = self.library.issue_book(isbn, member_id)
            title = self.library.get_book(loan.isbn).title
            name = self.library.get_member(loan.member_id).name
            return f"Issued '{title}' to {name}, due back {loan.due_date.isoformat()}."

        self.app.perform(action)

    def return_book(self) -> None:
        """Return the chosen book; show the fine and who is next in the queue (FR5, FR6)."""
        isbn, member_id = first_token(self.book.get()), first_token(self.member.get())

        def action() -> str:
            fine = self.library.return_book(isbn, member_id)
            book = self.library.get_book(isbn)
            lines = [f"'{book.title}' returned."]
            lines.append(f"Fine due: £{fine:.2f}" if fine > 0 else "Returned on time - no fine.")
            next_id = self.library.next_in_queue(book.isbn)
            if next_id:
                member = self.library.members.get(next_id)
                lines.append(f"Next in the reservation queue: {member.name if member else ''} ({next_id}).")
            messagebox.showinfo("Book returned", "\n".join(lines), parent=self)
            return " ".join(lines)

        self.app.perform(action)


class ReservationsTab(BaseTab):
    """Reservations: reserve form and the FIFO queue of each book (FR6)."""

    title = "Reservations"
    COLUMNS: Sequence[Column] = (
        ("position", "Position", 70),
        ("member_id", "Member ID", 90),
        ("name", "Name", 200),
    )

    def __init__(self, parent: ttk.Notebook, app: "LibraryApp") -> None:
        super().__init__(parent, app)
        ttk.Label(self, text="Reservation queues (first in line is served first)").grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        # show="tree headings": one parent row per book, its queue as child rows
        table, self.tree = self.make_table(self, self.COLUMNS, show="tree headings")
        self.tree.heading("#0", text="Book", anchor="w")
        self.tree.column("#0", width=260, stretch=True)
        table.grid(row=1, column=0, sticky="nsew")

        form = ttk.LabelFrame(self, text="Reserve a book", padding=8)
        form.grid(row=1, column=1, sticky="n", padx=(10, 0))
        self.book = tk.StringVar()
        self.member = tk.StringVar()
        self.book_box = ttk.Combobox(form, textvariable=self.book, width=30)
        self.member_box = ttk.Combobox(form, textvariable=self.member, width=30)
        self.add_field(form, 0, "Book", self.book_box)
        self.add_field(form, 1, "Member", self.member_box)
        ttk.Label(form, text="Only books with no copies available\ncan be reserved.", foreground="gray").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(4, 0)
        )
        ttk.Button(form, text="Reserve", command=self.reserve).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

    def refresh(self) -> None:
        """Show each book's queue in order and update the dropdowns."""
        self.tree.delete(*self.tree.get_children())
        for book in self.library.sorted_books("title"):
            queue = self.library.reservation_queue(book.isbn)
            if not queue:
                continue
            parent = self.tree.insert(
                "", "end", iid=book.isbn, text=f"{book.title} ({book.isbn})", open=True,
                values=("", "", f"{len(queue)} waiting"),
            )
            for position, member_id in enumerate(queue, start=1):
                member = self.library.members.get(member_id)
                self.tree.insert(
                    parent, "end", iid=f"{book.isbn}|{member_id}",
                    values=(position, member_id, member.name if member else "?"),
                )
        if not self.tree.get_children():
            self.tree.insert("", "end", text="(no reservations)")
        self.book_box["values"] = book_choices(self.library)
        self.member_box["values"] = member_choices(self.library)

    def reserve(self) -> None:
        """Add the chosen member to the chosen book's queue (FR6)."""
        isbn, member_id = first_token(self.book.get()), first_token(self.member.get())

        def action() -> str:
            position = self.library.reserve_book(isbn, member_id)
            title = self.library.get_book(isbn).title
            return f"Reserved '{title}' for {member_id.upper()}: position {position} in the queue."

        self.app.perform(action)


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
TAB_CLASSES: List[Type[BaseTab]] = [BooksTab, MembersTab, LoansTab, ReservationsTab]


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
