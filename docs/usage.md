# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run second_brain                          # production defaults
uv run --env-file .env second_brain          # dev settings
```

Or as a Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

| Variable    | Default    | Description                          |
|-------------|------------|--------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`  | `app.log`  | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

## Log Format

Console (stderr) output uses a compact format:

```
2026-10-24 19:45:00 | INF | second_brain.app:main:29 | Hello from second_brain!
```

Fields: timestamp (no milliseconds) · level · `module:function:line` · message.
Levels are shown as three-letter abbreviations:

| Level      | Shown as |
|------------|----------|
| `TRACE`    | `TRC`    |
| `DEBUG`    | `DBG`    |
| `INFO`     | `INF`    |
| `SUCCESS`  | `SUC`    |
| `WARNING`  | `WRN`    |
| `ERROR`    | `ERR`    |
| `CRITICAL` | `CRT`    |

Custom levels show the first three characters of their name. Output is
colorized when stderr is a terminal and plain otherwise (e.g. when piped).

The log file (`LOG_FILE`) keeps loguru's default, more detailed format with
milliseconds and full level names.
