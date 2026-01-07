from unittest import mock
from app.combiner import process_album
import subprocess
import pytest

from unittest.mock import patch

from pathlib import Path


def test_process_album_no_audio(tmp_path):
    album = tmp_path / "album1"
    album.mkdir()

    result = process_album((str(album), "out.m4a", "album1"))
    assert result == "Skipped: album1 (No audio files)"


def test_process_album_success(tmp_path, mocker):
    album = tmp_path / "album1"
    album.mkdir()

    # add fake audio files
    (album / "01.mp3").write_text("audio")
    (album / "02.wav").write_text("audio")

    mock_run = mocker.patch("app.combiner.subprocess.run")

    result = process_album((str(album), "out.m4a", "album1"))
    assert result == "Success: album1"

    mock_run.assert_called_once()

    # Ensure list fles was cleaned up
    assert not any(p.name.startswith("list_") for p in album.iterdir())


def test_process_album_error(tmp_path, mocker):
    album = tmp_path / "album1"
    album.mkdir()

    # add fake audio files
    (album / "01.mp3").write_text("audio")

    mock_run = mocker.patch(
        "app.combiner.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "ffmpeg"),
    )

    result = process_album((str(album), "out.m4a", "album1"))

    mock_run.assert_called_once()
    assert result == "Error: album1"


def test_ffmpeg_command_created_properly(tmp_path, mocker):
    album = tmp_path / "album1"
    album.mkdir()

    (album / "01.mp3").write_text("audio")

    mock_run = mocker.patch("app.combiner.subprocess.run")

    process_album((str(album), "out.m4a", "album1"))

    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "ffmpeg"
    assert cmd[1] == "-y"
    assert cmd[-1] == "out.m4a"
