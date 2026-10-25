"""Textual TUI: note list on the left, markdown editor on the right."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, TextArea

from second_brain.notes import list_note_files, notes_dir, read_note, save_note


class SecondBrainApp(App):
    """Browse notes read-only, or create a new one in the editor."""

    TITLE = "second_brain"

    CSS = """
    #sidebar { width: 32; border-right: solid $primary; }
    #note-list { height: 1fr; }
    #create { width: 100%; }
    #editor { height: 1fr; }
    #actions { height: auto; }
    #actions Button { margin-right: 1; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield ListView(id="note-list")
                yield Button("Create", id="create", variant="primary")
            with Vertical(id="main"):
                yield TextArea("", language="markdown", read_only=True, id="editor")
                with Horizontal(id="actions"):
                    yield Button("Save", id="save", variant="success")
                    yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self._set_editing(False)
        self.refresh_notes()

    def refresh_notes(self) -> None:
        """Reload the note list from disk, newest first."""
        base_dir = notes_dir()
        files = list_note_files(base_dir) if base_dir.is_dir() else []
        note_list = self.query_one("#note-list", ListView)
        note_list.clear()
        note_list.extend(ListItem(Label(f.name), name=f.name) for f in files)
        self._files = {f.name: f for f in files}

    def _set_editing(self, editing: bool) -> None:
        editor = self.query_one("#editor", TextArea)
        editor.read_only = not editing
        self.query_one("#save", Button).display = editing
        self.query_one("#cancel", Button).display = editing
        self.query_one("#create", Button).display = not editing
        if editing:
            editor.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        path: Path | None = self._files.get(event.item.name or "")
        if path is None:
            return
        self._set_editing(False)
        self.query_one("#editor", TextArea).text = read_note(path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        editor = self.query_one("#editor", TextArea)
        match event.button.id:
            case "create":
                editor.text = ""
                self._set_editing(True)
            case "save":
                if not editor.text.strip():
                    self.notify("Nothing to save.", severity="warning")
                    return
                path = save_note(editor.text, notes_dir())
                logger.info("Saved note: {}", path)
                self._set_editing(False)
                self.refresh_notes()
                self.notify(f"Saved {path.name}")
            case "cancel":
                editor.text = ""
                self._set_editing(False)
