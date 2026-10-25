import os
import sys
from pathlib import Path

from loguru import logger

APP_NAME = "second_brain"
LOG_FILE_NAME = "app.log"
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
    `2026-10-24 19:45:00 | INF | second_brain.app:main:67 | Hello!`.
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


def log_file_path() -> Path:
    """Return the log file path.

    `LOG_FILE` wins when set and non-empty (`~` is expanded; a relative path
    stays relative to the current directory). Otherwise the file lives in the
    per-user XDG state directory, e.g. `~/.local/state/second_brain/app.log`.
    A relative or empty `XDG_STATE_HOME` is ignored, as the XDG spec requires.

    Returns:
        The log file path; absolute unless `LOG_FILE` is a relative path.
    """
    override = os.environ.get("LOG_FILE")
    if override:
        return Path(override).expanduser()
    xdg_state_home = Path(os.environ.get("XDG_STATE_HOME", ""))
    state_dir = (
        xdg_state_home if xdg_state_home.is_absolute() else Path.home() / ".local/state"
    )
    return state_dir / APP_NAME / LOG_FILE_NAME


def configure_logging() -> None:
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var),
      using the compact `stderr_format`
    - File handler at DEBUG level writing to `log_file_path()`, using loguru's
      default format. The parent directory is created with mode 0700. If the
      file cannot be set up, one warning is logged and the run continues
      without a file handler.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = log_file_path()
    logger.remove()
    logger.add(sys.stderr, level=log_level, format=stderr_format)
    try:
        log_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        logger.add(log_file, level="DEBUG", rotation="50 KB", retention=1)
    except OSError as error:
        logger.warning("Log file disabled, cannot use {}: {}", log_file, error)


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from second_brain!")
