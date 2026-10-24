import io
import re
from pathlib import Path

import pytest
from loguru import logger

from second_brain.app import CONSOLE_FORMAT, configure_logging, main


def console_line_pattern(
    level_code: str, function: str, message: str
) -> re.Pattern[str]:
    """Build a regex for one compact console log line.

    Args:
        level_code: Expected 3-letter level, e.g. ``"INF"``.
        function: Expected function name in the ``second_brain.app`` module.
        message: Expected log message (matched literally).

    Returns:
        Compiled multiline pattern matching the whole line.
    """
    return re.compile(
        r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d"
        rf" \| {level_code}"
        rf" \| second_brain\.app:{function}:\d+"
        rf" \| {re.escape(message)}$",
        re.MULTILINE,
    )


def test_main_logs_greeting(capfd: pytest.CaptureFixture[str]):
    # Act
    main()

    # Assert
    captured = capfd.readouterr()
    assert console_line_pattern("INF", "main", "Hello from second_brain!").search(
        captured.err
    )


def test_console_shows_warning_as_war(capfd: pytest.CaptureFixture[str]):
    # Arrange
    configure_logging()

    # Act
    logger.warning("disk almost full")

    # Assert
    captured = capfd.readouterr()
    # Logged from this test module, so only the level/separator shape is pinned.
    assert re.search(
        r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \| WAR \| .+ \| disk almost full$",
        captured.err,
        re.MULTILINE,
    )


def test_file_log_keeps_default_format(tmp_path: Path):
    # Arrange
    log_file = tmp_path / "test.log"

    # Act
    main()
    logger.remove()  # flush and close the file sink

    # Assert
    assert re.search(
        r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3} \| INFO     \| "
        r"second_brain\.app:main:\d+ - Hello from second_brain!$",
        log_file.read_text(),
        re.MULTILINE,
    )


def test_console_format_keeps_colors():
    # Arrange
    configure_logging()
    sink = io.StringIO()
    handler_id = logger.add(sink, format=CONSOLE_FORMAT, colorize=True)

    # Act
    logger.warning("colored")
    logger.remove(handler_id)

    # Assert
    output = sink.getvalue()
    assert "\x1b[32m" in output  # green timestamp
    assert re.search(r"\x1b\[[\d;]+m(?:\x1b\[[\d;]+m)*WAR\x1b\[0m", output)
