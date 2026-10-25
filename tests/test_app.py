import io
import os
import re
import sys

import pytest
from loguru import logger

from second_brain.app import (
    configure_logging,
    default_log_dir,
    log_file_path,
    main,
    stderr_format,
)

STDERR_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| "
    r"second_brain\.app:main:\d+ \| Hello from second_brain!$"
)


def test_main_logs_greeting(capfd):
    main()
    captured = capfd.readouterr()
    assert "Hello from second_brain!" in captured.err


def test_stderr_line_format(capfd):
    main()
    lines = capfd.readouterr().err.splitlines()
    assert any(STDERR_LINE.match(line) for line in lines), lines


@pytest.mark.parametrize(
    ("level", "short"),
    [
        ("TRACE", "TRC"),
        ("DEBUG", "DBG"),
        ("INFO", "INF"),
        ("SUCCESS", "SUC"),
        ("WARNING", "WRN"),
        ("ERROR", "ERR"),
        ("CRITICAL", "CRT"),
    ],
)
def test_level_short_names(capfd, monkeypatch, level, short):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()
    logger.log(level, "level check")
    err = capfd.readouterr().err
    assert f" | {short} | " in err
    assert f" | {level}" not in err


def test_custom_level_falls_back_to_first_three_chars(capfd):
    logger.level("NOTICE_T", no=25)
    configure_logging()
    logger.log("NOTICE_T", "custom level")
    assert " | NOT | " in capfd.readouterr().err


@pytest.mark.parametrize("name", ["{<x", "<b>X", "{0}"])
def test_custom_level_with_markup_chars_does_not_crash(capfd, name):
    logger.level(name, no=26)
    configure_logging()
    logger.log(name, "odd level")
    err = capfd.readouterr().err
    assert f" | {name[:3]} | " in err
    assert "odd level" in err


def test_exception_still_rendered(capfd):
    configure_logging()

    @logger.catch
    def boom():
        return 1 / 0

    boom()
    err = capfd.readouterr().err
    assert " | ERR | " in err
    assert "Traceback" in err
    assert "ZeroDivisionError" in err


def test_colors_on_tty_like_sink():
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=True)
    logger.info("colored")
    assert "\x1b[" in sink.getvalue()


def test_no_colors_when_not_colorized():
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=False)
    logger.info("plain")
    assert "\x1b[" not in sink.getvalue()


def test_log_file_format_unchanged():
    main()
    logger.remove()
    with open(os.environ["LOG_FILE"]) as f:
        content = f.read()
    assert re.search(
        r"\d{2}:\d{2}:\d{2}\.\d{3} \| INFO     \| "
        r"second_brain\.app:main:\d+ - Hello from second_brain!",
        content,
    ), content


# ---------------------------------------------------------------------------
# Log file location
# ---------------------------------------------------------------------------


def test_default_log_dir_is_per_user(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    if sys.platform == "darwin":
        expected = tmp_path / "Library" / "Logs" / "second_brain"
    elif sys.platform.startswith("linux"):
        expected = tmp_path / ".local" / "state" / "second_brain" / "log"
    else:
        pytest.skip("unsupported platform")
    assert default_log_dir() == expected


def test_log_file_path_defaults_to_app_log_in_log_dir(tmp_log_dir):
    assert log_file_path() == tmp_log_dir / "app.log"


@pytest.mark.parametrize("name", ["dev.log", "sub/dev.log"])
def test_log_file_path_relative_resolves_against_log_dir(
    tmp_log_dir, monkeypatch, name
):
    monkeypatch.setenv("LOG_FILE", name)
    assert log_file_path() == tmp_log_dir / name


def test_log_file_path_absolute_is_used_as_is(tmp_log_dir, tmp_path, monkeypatch):
    target = tmp_path / "elsewhere" / "x.log"
    monkeypatch.setenv("LOG_FILE", str(target))
    assert log_file_path() == target


def test_log_file_path_expands_tilde(tmp_log_dir, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("LOG_FILE", "~/sb.log")
    assert log_file_path() == tmp_path / "sb.log"


def test_log_file_path_empty_falls_back_to_default(tmp_log_dir, monkeypatch):
    monkeypatch.setenv("LOG_FILE", "")
    assert log_file_path() == tmp_log_dir / "app.log"


def test_configure_logging_ignores_cwd_and_creates_log_dir(
    tmp_log_dir, tmp_path, monkeypatch
):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    assert not tmp_log_dir.exists()
    configure_logging()
    logger.info("where does this go")
    logger.remove()
    assert "where does this go" in (tmp_log_dir / "app.log").read_text()
    assert not (cwd / "app.log").exists()


def test_file_sink_rotation_and_retention(tmp_log_dir, monkeypatch):
    calls = []
    real_add = logger.add

    def spy(sink, **kwargs):
        calls.append((sink, kwargs))
        return real_add(sink, **kwargs)

    monkeypatch.setattr(logger, "add", spy)
    configure_logging()
    logger.remove()
    file_kwargs = [kw for sink, kw in calls if sink == tmp_log_dir / "app.log"]
    assert len(file_kwargs) == 1
    assert file_kwargs[0]["level"] == "DEBUG"
    assert file_kwargs[0]["rotation"] == "10 MB"
    assert file_kwargs[0]["retention"] == "14 days"
