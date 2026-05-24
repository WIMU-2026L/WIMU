"""Unit tests for CLaMP3 output parsing and result saving."""


import pytest

from metrics.clamp3 import _copy_midi_files, _save_results
from metrics.wandb_logger import _parse_clamp3_score


class TestParseClamp3Score:
    def test_parses_standard_output(self):
        output = "CLaMP3 Score: 0.7423\nSome other line"
        assert _parse_clamp3_score(output) == pytest.approx(0.7423)

    def test_parses_with_extra_whitespace(self):
        output = "CLaMP3  Score :  0.5000"
        assert _parse_clamp3_score(output) == pytest.approx(0.5)

    def test_returns_none_when_not_found(self):
        assert _parse_clamp3_score("No score here") is None

    def test_returns_none_for_empty_string(self):
        assert _parse_clamp3_score("") is None

    def test_case_insensitive(self):
        output = "clamp3 score: 0.9"
        assert _parse_clamp3_score(output) == pytest.approx(0.9)


class TestSaveResults:
    def test_writes_sections_to_file(self, tmp_path):
        results = {"classical/angry": "CLaMP3 Score: 0.75\n"}
        out_file = tmp_path / "results.txt"

        _save_results(results, out_file)

        content = out_file.read_text(encoding="utf-8")
        assert "=== classical/angry ===" in content
        assert "CLaMP3 Score: 0.75" in content

    def test_writes_multiple_sections(self, tmp_path):
        results = {"jazz/happy": "score 0.8", "rock/sad": "score 0.6"}
        out_file = tmp_path / "results.txt"

        _save_results(results, out_file)

        content = out_file.read_text(encoding="utf-8")
        assert "=== jazz/happy ===" in content
        assert "=== rock/sad ===" in content

    def test_section_suffix_is_appended(self, tmp_path):
        results = {"classical": "output"}
        out_file = tmp_path / "results.txt"

        _save_results(results, out_file, section_suffix="[all vibes]")

        content = out_file.read_text(encoding="utf-8")
        assert "=== classical [all vibes] ===" in content


class TestCopyMidiFiles:
    def test_copies_mid_files(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        (src / "track1.mid").write_bytes(b"")
        (src / "track2.mid").write_bytes(b"")

        count = _copy_midi_files(src, dst)

        assert count == 2
        assert (dst / "track1.mid").exists()
        assert (dst / "track2.mid").exists()

    def test_prefix_is_applied(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        (src / "track.mid").write_bytes(b"")

        _copy_midi_files(src, dst, prefix="angry_")

        assert (dst / "angry_track.mid").exists()

    def test_non_midi_files_are_skipped(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        (src / "notes.txt").write_text("text")
        (src / "track.mid").write_bytes(b"")

        count = _copy_midi_files(src, dst)

        assert count == 1
        assert not (dst / "notes.txt").exists()
