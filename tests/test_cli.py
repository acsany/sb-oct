"""Tests for the CLI (Click group + new subcommand)."""

import re
from pathlib import Path

from click.testing import CliRunner

from second_brain.cli import cli

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

runner = CliRunner()


# ---------------------------------------------------------------------------
# new subcommand
# ---------------------------------------------------------------------------


def test_cli_new_creates_file(tmp_note_dir):
    result = runner.invoke(cli, ["new", "Test idea"])
    assert result.exit_code == 0
    files = list(tmp_note_dir.glob("*.md"))
    assert len(files) == 1


def test_cli_new_prints_path_to_stdout(tmp_note_dir):
    result = runner.invoke(cli, ["new", "Test idea"])
    assert result.exit_code == 0
    output = result.output.strip().splitlines()[-1]
    assert output.endswith(".md")
    assert Path(output).is_file()


def test_cli_new_uses_env_var_for_dir(tmp_note_dir):
    result = runner.invoke(cli, ["new", "Test idea"])
    assert result.exit_code == 0
    assert tmp_note_dir.is_dir()
    files = list(tmp_note_dir.glob("*.md"))
    assert len(files) == 1


def test_cli_new_default_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("SECOND_BRAIN_DIR", raising=False)
    fake_home = tmp_path / "fakehome"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", staticmethod(lambda: fake_home))
    result = runner.invoke(cli, ["new", "Test idea"])
    assert result.exit_code == 0
    expected_dir = fake_home / "second_brain"
    assert expected_dir.is_dir()
    files = list(expected_dir.glob("*.md"))
    assert len(files) == 1


def test_cli_new_missing_title_shows_error():
    result = runner.invoke(cli, ["new"])
    assert result.exit_code != 0
    assert "Missing argument" in result.output


def test_cli_new_file_content_has_heading(tmp_note_dir):
    result = runner.invoke(cli, ["new", "My heading test"])
    assert result.exit_code == 0
    md_file = next(tmp_note_dir.glob("*.md"))
    lines = md_file.read_text().splitlines()
    assert lines[0] == "# My heading test"


def test_cli_new_file_content_has_timestamp(tmp_note_dir):
    result = runner.invoke(cli, ["new", "Timestamp test"])
    assert result.exit_code == 0
    md_file = next(tmp_note_dir.glob("*.md"))
    text = md_file.read_text()
    assert re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", text)


# ---------------------------------------------------------------------------
# help
# ---------------------------------------------------------------------------


def test_cli_group_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "second_brain" in result.output or "capture" in result.output


def test_cli_new_help():
    result = runner.invoke(cli, ["new", "--help"])
    assert result.exit_code == 0
    assert "TITLE" in result.output


def test_cli_new_folds_accents_in_filename(tmp_note_dir):
    result = runner.invoke(cli, ["new", "Café über Ideen"])
    assert result.exit_code == 0
    assert "cafe-uber-ideen" in next(tmp_note_dir.glob("*.md")).name


# ---------------------------------------------------------------------------
# list subcommand
# ---------------------------------------------------------------------------


def test_cli_list_shows_directory_header(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    (tmp_note_dir / "20260322-note.md").write_text("# Note\n")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert f"Notes: {tmp_note_dir}" in result.output


def test_cli_list_shows_numbered_files(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    (tmp_note_dir / "20260320-a.md").write_text("# A\n")
    (tmp_note_dir / "20260321-b.md").write_text("# B\n")
    (tmp_note_dir / "20260322-c.md").write_text("# C\n")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "1." in result.output
    assert "2." in result.output
    assert "3." in result.output


def test_cli_list_sorted_newest_first(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    (tmp_note_dir / "20260320-old.md").write_text("# Old\n")
    (tmp_note_dir / "20260322-new.md").write_text("# New\n")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    numbered = [ln for ln in lines if re.match(r"^\d+\.", ln)]
    assert "20260322-new.md" in numbered[0]
    assert "20260320-old.md" in numbered[1]


def test_cli_list_empty_directory(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No notes found" in result.output


def test_cli_list_missing_directory(tmp_note_dir):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_cli_list_ignores_non_md_files(tmp_note_dir):
    tmp_note_dir.mkdir(parents=True)
    (tmp_note_dir / "20260322-note.md").write_text("# Note\n")
    (tmp_note_dir / "20260322-other.txt").write_text("not a note\n")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "20260322-note.md" in result.output
    assert "20260322-other.txt" not in result.output


def test_cli_list_help():
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    assert "List" in result.output or "list" in result.output
