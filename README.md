# second-brain

## Installation

1. Clone the repository.
2. Install dependencies:

```bash
uv sync
```

## Usage

Via the CLI entrypoint:

```bash
uv run second_brain
```

With the dev environment:

```bash
uv run --env-file .env second_brain
```

Via the Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

`.env.example` is the template — copy it to `.env` for development:

```bash
cp .env.example .env
```

- `LOG_LEVEL` — default: `INFO`. Set to `DEBUG` in `.env` for verbose console output.
- `LOG_FILE` — default: `app.log`. Path to the log file.

Note that `uv run --env-file .env` loads the dev environment explicitly (no auto-loading).

## Log Format

Console (stderr) lines are compact, with three-letter level names (`TRC`, `DBG`, `INF`, `SUC`, `WRN`, `ERR`, `CRT`):

```
2026-10-24 19:45:00 | INF | second_brain.app:main:29 | Hello from second_brain!
```

The log file (`LOG_FILE`) keeps loguru's default format with milliseconds. See [docs/usage.md](docs/usage.md#log-format) for details.

## Testing

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```
