"""Unit tests for data.dataset_processing."""

import shutil
import tempfile
from pathlib import Path

import pytest

from data.dataset_processing import organize_midi_files


@pytest.fixture()
def tmp_dirs():
    """Provide temporary source and output directories, cleaned up after the test."""
    src = Path(tempfile.mkdtemp())
    dst = Path(tempfile.mkdtemp())
    yield src, dst
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dst, ignore_errors=True)


def _make_midi(directory: Path, name: str) -> Path:
    """Create a dummy (empty) MIDI file."""
    f = directory / name
    f.write_bytes(b"")
    return f


class TestOrganizeMidiFiles:
    def test_valid_file_is_placed_in_correct_directory(self, tmp_dirs):
        src, dst = tmp_dirs
        _make_midi(src, "XMIDI_angry_classical_001.midi")

        organize_midi_files(src, dst)

        assert (dst / "classical" / "angry" / "XMIDI_angry_classical_001.midi").exists()

    def test_multiple_files_are_organized(self, tmp_dirs):
        src, dst = tmp_dirs
        files = [
            "XMIDI_happy_jazz_001.midi",
            "XMIDI_sad_rock_002.midi",
            "XMIDI_angry_classical_003.midi",
        ]
        for name in files:
            _make_midi(src, name)

        organize_midi_files(src, dst)

        assert (dst / "jazz" / "happy" / "XMIDI_happy_jazz_001.midi").exists()
        assert (dst / "rock" / "sad" / "XMIDI_sad_rock_002.midi").exists()
        assert (dst / "classical" / "angry" / "XMIDI_angry_classical_003.midi").exists()

    def test_invalid_filename_is_skipped(self, tmp_dirs):
        src, dst = tmp_dirs
        _make_midi(src, "unknown_format.midi")

        organize_midi_files(src, dst)

        # Destination should remain empty
        assert not any(dst.rglob("*.midi"))

    def test_original_files_are_not_modified(self, tmp_dirs):
        src, dst = tmp_dirs
        original = _make_midi(src, "XMIDI_warm_pop_005.midi")

        organize_midi_files(src, dst)

        assert original.exists(), "Source file should not be removed"

    def test_non_midi_files_are_ignored(self, tmp_dirs):
        src, dst = tmp_dirs
        (src / "notes.txt").write_text("some text")
        _make_midi(src, "XMIDI_lazy_country_010.midi")

        organize_midi_files(src, dst)

        assert not any(dst.rglob("*.txt"))
        assert (dst / "country" / "lazy" / "XMIDI_lazy_country_010.midi").exists()
