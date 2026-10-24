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

## Logging

Console (stderr) lines use a compact format: no milliseconds, a 3-letter level code
(`DEB`, `INF`, `WAR`, `ERR`, ...) and `|` before the message. Colors are kept on a tty.

```
2026-10-24 12:00:00 | INF | second_brain.app:main:42 | Hello from second_brain!
```

The file log (`LOG_FILE`) keeps loguru's default format.
