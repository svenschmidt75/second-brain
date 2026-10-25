import io
import os
import re
import stat
from pathlib import Path

import pytest
from loguru import logger

from second_brain.app import configure_logging, log_file_path, main, stderr_format

STDERR_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| "
    r"second_brain\.app:main:\d+ \| Hello from second_brain!$"
)


def test_main_logs_greeting(capfd):
    # Act
    main()

    # Assert
    captured = capfd.readouterr()
    assert "Hello from second_brain!" in captured.err


def test_stderr_line_format(capfd):
    # Act
    main()

    # Assert
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
    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    configure_logging()

    # Act
    logger.log(level, "level check")

    # Assert
    err = capfd.readouterr().err
    assert f" | {short} | " in err
    assert f" | {level}" not in err


def test_custom_level_falls_back_to_first_three_chars(capfd):
    # Arrange
    logger.level("NOTICE_T", no=25)
    configure_logging()

    # Act
    logger.log("NOTICE_T", "custom level")

    # Assert
    assert " | NOT | " in capfd.readouterr().err


@pytest.mark.parametrize("name", ["{<x", "<b>X", "{0}"])
def test_custom_level_with_markup_chars_does_not_crash(capfd, name):
    # Arrange
    logger.level(name, no=26)
    configure_logging()

    # Act
    logger.log(name, "odd level")

    # Assert
    err = capfd.readouterr().err
    assert f" | {name[:3]} | " in err
    assert "odd level" in err


def test_exception_still_rendered(capfd):
    # Arrange
    configure_logging()

    @logger.catch
    def boom():
        return 1 / 0

    # Act
    boom()

    # Assert
    err = capfd.readouterr().err
    assert " | ERR | " in err
    assert "Traceback" in err
    assert "ZeroDivisionError" in err


def test_colors_on_tty_like_sink():
    # Arrange
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=True)

    # Act
    logger.info("colored")

    # Assert
    assert "\x1b[" in sink.getvalue()


def test_no_colors_when_not_colorized():
    # Arrange
    sink = io.StringIO()
    logger.remove()
    logger.add(sink, format=stderr_format, colorize=False)

    # Act
    logger.info("plain")

    # Assert
    assert "\x1b[" not in sink.getvalue()


def test_log_file_format_unchanged():
    # Act
    main()
    logger.remove()  # flush and close the file sink

    # Assert
    with open(os.environ["LOG_FILE"]) as f:
        content = f.read()
    assert re.search(
        r"\d{2}:\d{2}:\d{2}\.\d{3} \| INFO     \| "
        r"second_brain\.app:main:\d+ - Hello from second_brain!",
        content,
    ), content


@pytest.mark.parametrize("xdg", [None, "", "relative/state"])
def test_log_file_path_default(default_log_env, monkeypatch, xdg):
    # Arrange
    if xdg is not None:
        monkeypatch.setenv("XDG_STATE_HOME", xdg)

    # Act
    path = log_file_path()

    # Assert
    assert path == default_log_env / ".local/state/second_brain/app.log"
    assert path.is_absolute()


def test_log_file_path_honors_absolute_xdg_state_home(
    default_log_env, tmp_path, monkeypatch
):
    # Arrange
    xdg = tmp_path / "xdg"
    monkeypatch.setenv("XDG_STATE_HOME", str(xdg))

    # Act
    path = log_file_path()

    # Assert
    assert path == xdg / "second_brain/app.log"


@pytest.mark.parametrize(
    ("log_file", "expected"),
    [
        ("{tmp}/custom/x.log", "{tmp}/custom/x.log"),
        ("~/logs/x.log", "{home}/logs/x.log"),
        ("app.log", "app.log"),
        ("", "{tmp}/xdg/second_brain/app.log"),
    ],
)
def test_log_file_path_override(
    default_log_env, tmp_path, monkeypatch, log_file, expected
):
    # Arrange
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg"))
    monkeypatch.setenv("LOG_FILE", log_file.format(tmp=tmp_path, home=default_log_env))

    # Act
    path = log_file_path()

    # Assert
    assert path == Path(expected.format(tmp=tmp_path, home=default_log_env))


def test_configure_logging_creates_private_log_dir(default_log_env):
    # Act
    configure_logging()

    # Assert
    log_dir = default_log_env / ".local/state/second_brain"
    assert stat.S_IMODE(log_dir.stat().st_mode) == 0o700
    assert (log_dir / "app.log").is_file()


def test_unwritable_log_location_warns_and_continues(tmp_path, monkeypatch, capfd):
    # Arrange
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory")
    log_file = blocker / "app.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    # Act
    configure_logging()
    logger.info("still logging")

    # Assert
    err = capfd.readouterr().err
    assert " | WRN | " in err
    assert str(log_file) in err
    assert "still logging" in err
