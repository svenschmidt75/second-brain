# second-brain

## Installation

1. Clone the repository.
2. Install dependencies:

```bash
uv sync
```

## Usage

```bash
uv run second_brain                          # CLI entrypoint
uv run --env-file .env second_brain          # with dev environment
uv run python -m second_brain                # as a Python module
```

## Environment Variables

`.env.example` is the template — copy it to `.env` for development:

```bash
cp .env.example .env
```

- `LOG_LEVEL` (default: `INFO`) — console log level; set to `DEBUG` in `.env` for verbose console output.
- `LOG_FILE` (default: `app.log`) — path to the log file.

`uv run --env-file .env` loads the dev environment explicitly (no auto-loading).

## Logging

Console (stderr) lines use a compact format: no milliseconds, a 3-letter level code
(`DEB`, `INF`, `WAR`, `ERR`, ...) and `|` before the message. Colors are kept on a tty.

```
2026-10-24 12:00:00 | INF | second_brain.app:main:42 | Hello from second_brain!
```

The file log (`LOG_FILE`) keeps loguru's default format.

## Testing

```bash
uv run pytest              # run tests
uv run pytest --cov        # run tests with coverage
```

## Documentation

```bash
uv run python scripts/serve_docs.py    # preview docs locally
uv run mkdocs build                    # build static docs
```
