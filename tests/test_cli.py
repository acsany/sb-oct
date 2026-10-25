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
