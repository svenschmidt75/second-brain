"""Shared test fixtures."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _test_log_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))


@pytest.fixture
def tmp_note_dir(tmp_path, monkeypatch):
    """Redirect SECOND_BRAIN_DIR to a temporary directory for tests."""
    d = tmp_path / "notes"
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(d))
    return d


@pytest.fixture
def default_log_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Unset LOG_FILE and XDG_STATE_HOME and point HOME at a temp directory.

    Returns:
        The fake home directory.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.delenv("LOG_FILE", raising=False)
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(home))
    return home
