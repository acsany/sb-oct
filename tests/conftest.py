"""Shared test fixtures."""

import pytest


@pytest.fixture(autouse=True)
def _test_log_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))


@pytest.fixture
def tmp_note_dir(tmp_path, monkeypatch):
    """Redirect SECOND_BRAIN_DIR to a temporary directory for tests."""
    d = tmp_path / "notes"
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(d))
    return d


@pytest.fixture
def tmp_log_dir(tmp_path, monkeypatch):
    """Redirect the per-user log directory to a temporary one and unset LOG_FILE."""
    d = tmp_path / "logs"
    monkeypatch.setattr("second_brain.app.default_log_dir", lambda: d)
    monkeypatch.delenv("LOG_FILE", raising=False)
    return d
