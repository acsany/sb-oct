"""Tests for the Textual TUI."""

from click.testing import CliRunner
from textual.widgets import Button, ListView, TextArea

from second_brain.cli import cli
from second_brain.tui import SecondBrainApp


def _make_notes(d):
    d.mkdir(parents=True, exist_ok=True)
    (d / "2026-01-01-old.md").write_text("# Old\n", encoding="utf-8")
    (d / "2026-01-02-new.md").write_text("# New\n\nhello\n", encoding="utf-8")


async def test_lists_notes_newest_first(tmp_note_dir):
    _make_notes(tmp_note_dir)
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        items = list(app.query_one("#note-list", ListView).children)
        assert [i.name for i in items] == ["2026-01-02-new.md", "2026-01-01-old.md"]


async def test_initial_state_is_read_only_without_save_cancel(tmp_note_dir):
    _make_notes(tmp_note_dir)
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one("#editor", TextArea).read_only
        assert not app.query_one("#save", Button).display
        assert not app.query_one("#cancel", Button).display
        assert app.query_one("#create", Button).display


async def test_selecting_note_shows_content_read_only(tmp_note_dir):
    _make_notes(tmp_note_dir)
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        lv = app.query_one("#note-list", ListView)
        lv.focus()
        await pilot.press("down", "enter")
        await pilot.pause()
        editor = app.query_one("#editor", TextArea)
        assert editor.text == "# New\n\nhello\n"
        assert editor.read_only


async def test_create_enters_edit_mode_and_save_writes_note(tmp_note_dir):
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.click("#create")
        await pilot.pause()
        editor = app.query_one("#editor", TextArea)
        assert not editor.read_only
        assert app.query_one("#save", Button).display
        assert app.query_one("#cancel", Button).display
        editor.text = "# Fresh\n\nbody"
        await pilot.click("#save")
        await pilot.pause()
        files = list(tmp_note_dir.glob("*.md"))
        assert len(files) == 1
        assert files[0].read_text(encoding="utf-8").startswith("# Fresh")
        assert editor.read_only
        assert len(app.query_one("#note-list", ListView).children) == 1


async def test_cancel_discards_without_writing(tmp_note_dir):
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.click("#create")
        await pilot.pause()
        app.query_one("#editor", TextArea).text = "# Nope"
        await pilot.click("#cancel")
        await pilot.pause()
        assert not tmp_note_dir.exists() or not list(tmp_note_dir.glob("*.md"))
        assert app.query_one("#editor", TextArea).read_only
        assert not app.query_one("#save", Button).display


def test_cli_without_arguments_launches_tui(monkeypatch):
    called = []
    monkeypatch.setattr(SecondBrainApp, "run", lambda self, *a, **k: called.append(1))
    result = CliRunner().invoke(cli, [])
    assert result.exit_code == 0
    assert called == [1]


def test_cli_subcommand_does_not_launch_tui(monkeypatch, tmp_note_dir):
    called = []
    monkeypatch.setattr(SecondBrainApp, "run", lambda self, *a, **k: called.append(1))
    CliRunner().invoke(cli, ["list"])
    assert called == []
