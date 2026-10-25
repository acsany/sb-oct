import os
import sys
from pathlib import Path

from loguru import logger
from platformdirs import user_log_path

APP_NAME = "second_brain"
DEFAULT_LOG_FILE = "app.log"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "14 days"

LEVEL_SHORT_NAMES = {
    "TRACE": "TRC",
    "DEBUG": "DBG",
    "INFO": "INF",
    "SUCCESS": "SUC",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}


def stderr_format(record: dict) -> str:
    """Build the compact loguru format template for the stderr sink.

    Produces lines like
    `2026-10-24 19:45:00 | INF | second_brain.app:main:29 | Hello!`.
    Built-in levels map to three-letter names via `LEVEL_SHORT_NAMES`; custom
    levels fall back to the first three characters of their name.

    Args:
        record: The loguru record dict of the message being logged.

    Returns:
        A format template ending with `\\n{exception}`, as loguru requires
            for callable formats.
    """
    # Unknown names are substituted at render time rather than embedded in the
    # template, so braces or markup tags in a custom level name stay literal.
    short = LEVEL_SHORT_NAMES.get(record["level"].name, "{level.name:.3}")
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        f"<level>{short}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>\n{exception}"
    )


def default_log_dir() -> Path:
    """Return the per-user log directory.

    This is `~/Library/Logs/second_brain` on macOS,
    `$XDG_STATE_HOME/second_brain/log` (default `~/.local/state/second_brain/log`)
    on Linux and `%LOCALAPPDATA%\\second_brain\\Logs` on Windows.
    `appauthor=False` keeps platformdirs from repeating the app name as the
    author on Windows.

    Returns:
        The log directory. It may not exist yet.
    """
    return user_log_path(APP_NAME, appauthor=False)


def log_file_path() -> Path:
    """Resolve the log file path from the LOG_FILE environment variable.

    `~` is expanded first. Absolute paths are used as is; relative paths are
    resolved against `default_log_dir()`. An unset or empty LOG_FILE means
    `app.log`. The variable is read on every call.

    Returns:
        The path of the log file.
    """
    path = Path(os.environ.get("LOG_FILE") or DEFAULT_LOG_FILE).expanduser()
    return path if path.is_absolute() else default_log_dir() / path


def configure_logging(console: bool = True):
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler (skipped when `console` is false, e.g. while the TUI owns
      the terminal) at LOG_LEVEL (default: INFO, configurable via env var),
      using the compact `stderr_format`
    - File handler at DEBUG level writing to `log_file_path()` (by default
      `app.log` in the per-user log directory, which is created if missing),
      using loguru's default format, rotating at 10 MB and keeping rotated
      files for 14 days

    Args:
        console: Whether to log to stderr as well as the file.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = log_file_path()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    if console:
        logger.add(sys.stderr, level=log_level, format=stderr_format)
    logger.add(log_file, level="DEBUG", rotation=LOG_ROTATION, retention=LOG_RETENTION)


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from second_brain!")
