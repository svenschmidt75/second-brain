"""Tests for the Textual TUI."""

import pytest
from textual.widgets import Button, ListView, TextArea

from second_brain.cli import cli
from second_brain.notes import create_note
from second_brain.tui import NoteListItem, SecondBrainApp


@pytest.mark.asyncio
async def test_selecting_note_shows_content_read_only(tmp_note_dir):
    # Arrange
    create_note("Alpha", tmp_note_dir, body="alpha body")
    app = SecondBrainApp()

    # Act
    async with app.run_test() as pilot:
        await pilot.pause()
        editor = app.query_one("#editor", TextArea)

        # Assert
        assert len(app.query_one("#note-list", ListView)) == 1
        assert "alpha body" in editor.text
        assert editor.read_only


@pytest.mark.asyncio
async def test_create_save_adds_note_and_leaves_edit_mode(tmp_note_dir):
    # Arrange
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Act
        await pilot.click("#create")
        editor = app.query_one("#editor", TextArea)
        assert not editor.read_only
        editor.load_text("# New idea\nsome body")
        await pilot.click("#save")
        await pilot.pause()

        # Assert
        files = list(tmp_note_dir.glob("*.md"))
        assert len(files) == 1
        assert files[0].read_text().startswith("# New idea\n\nsome body")
        assert editor.read_only
        assert not app.query_one("#create", Button).disabled


@pytest.mark.asyncio
async def test_cancel_discards_and_restores_note(tmp_note_dir):
    # Arrange
    create_note("Alpha", tmp_note_dir, body="alpha body")
    app = SecondBrainApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Act
        await pilot.click("#create")
        editor = app.query_one("#editor", TextArea)
        editor.load_text("draft")
        await pilot.click("#cancel")
        await pilot.pause()

        # Assert
        assert len(list(tmp_note_dir.glob("*.md"))) == 1
        assert editor.read_only
        assert "alpha body" in editor.text
        assert isinstance(
            app.query_one("#note-list", ListView).highlighted_child, NoteListItem
        )


def test_cli_without_command_launches_tui(monkeypatch):
    # Arrange
    from click.testing import CliRunner

    launched = []
    monkeypatch.setattr("second_brain.tui.run_tui", lambda: launched.append(True))

    # Act
    result = CliRunner().invoke(cli, [])

    # Assert
    assert result.exit_code == 0
    assert launched == [True]
