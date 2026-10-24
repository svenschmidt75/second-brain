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
