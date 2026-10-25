"""Textual TUI: note list on the left, markdown editor on the right."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, TextArea

from second_brain.notes import create_note, list_note_files, notes_dir, read_note


class NoteListItem(ListItem):
    """List row that remembers the note file it shows."""

    def __init__(self, path: Path) -> None:
        super().__init__(Label(path.stem))
        self.path = path


class SecondBrainApp(App[None]):
    """Browse notes read-only; create new ones in edit mode."""

    TITLE = "second_brain"
    CSS = """
    #sidebar { width: 32; border-right: solid $primary; }
    #note-list { height: 1fr; }
    #create { width: 100%; }
    #main { width: 1fr; }
    #editor { height: 1fr; }
    #edit-buttons { height: auto; display: none; }
    #edit-buttons.editing { display: block; }
    """
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield ListView(id="note-list")
                yield Button("Create", id="create", variant="primary")
            with Vertical(id="main"):
                yield TextArea.code_editor(
                    "", language="markdown", read_only=True, id="editor"
                )
                with Horizontal(id="edit-buttons"):
                    yield Button("Save", id="save", variant="success")
                    yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_notes()

    async def refresh_notes(self, select: Path | None = None) -> None:
        """Reload the note list from the notes directory, newest first.

        Args:
            select: Note to highlight afterwards; the first note if absent.
        """
        note_list = self.query_one("#note-list", ListView)
        await note_list.clear()
        base_dir = notes_dir()
        files = list_note_files(base_dir) if base_dir.is_dir() else []
        await note_list.extend(NoteListItem(path) for path in files)
        if files:
            resolved = [f.resolve() for f in files]
            note_list.index = resolved.index(select) if select in resolved else 0

    def _set_editing(self, editing: bool) -> None:
        editor = self.query_one("#editor", TextArea)
        editor.read_only = not editing
        self.query_one("#edit-buttons").set_class(editing, "editing")
        self.query_one("#create", Button).disabled = editing
        self.query_one("#note-list", ListView).disabled = editing
        if editing:
            editor.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if isinstance(event.item, NoteListItem):
            self.query_one("#editor", TextArea).load_text(read_note(event.item.path))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.query_one("#editor", TextArea).load_text("")
            self._set_editing(True)
        elif event.button.id == "save":
            self.run_worker(self._save(), exclusive=True)
        elif event.button.id == "cancel":
            self._set_editing(False)
            selected = self.query_one("#note-list", ListView).highlighted_child
            text = (
                read_note(selected.path) if isinstance(selected, NoteListItem) else ""
            )
            self.query_one("#editor", TextArea).load_text(text)

    async def _save(self) -> None:
        text = self.query_one("#editor", TextArea).text.strip()
        if not text:
            self.notify("Nothing to save", severity="warning")
            return
        # A leading markdown '#' is dropped: create_note writes the heading itself.
        first, _, rest = text.partition("\n")
        title = first.lstrip("#").strip() or "untitled"
        path = create_note(title, notes_dir(), body=rest)
        logger.info("Created note: {}", path)
        self._set_editing(False)
        await self.refresh_notes(select=path)
        self.notify(f"Saved {path.name}")


def run_tui() -> None:
    """Launch the TUI."""
    SecondBrainApp().run()
