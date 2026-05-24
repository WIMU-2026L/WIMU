"""Unit tests for CLaMP3 output parsing and result saving."""

import pytest

from metrics.clamp3 import _copy_midi_files, _parse_clamp3_output, _save_results
from metrics.wandb_logger import _parse_clamp3_score

_SAMPLE_OUTPUT = (
    "Total query features: 10\n"
    "Total reference features: 100\n"
    "Group similarity: 0.7423\n"
)


class TestParseClamp3Output:
    def test_extracts_score(self):
        parsed = _parse_clamp3_output(_SAMPLE_OUTPUT)
        assert parsed["score"] == pytest.approx(0.7423)

    def test_extracts_query_count(self):
        parsed = _parse_clamp3_output(_SAMPLE_OUTPUT)
        assert parsed["query_n"] == 10

    def test_extracts_ref_count(self):
        parsed = _parse_clamp3_output(_SAMPLE_OUTPUT)
        assert parsed["ref_n"] == 100

    def test_returns_none_when_score_missing(self):
        parsed = _parse_clamp3_output("No score here")
        assert parsed["score"] is None

    def test_returns_none_for_empty_string(self):
        parsed = _parse_clamp3_output("")
        assert parsed["score"] is None
        assert parsed["query_n"] is None
        assert parsed["ref_n"] is None


class TestParseClamp3Score:
    def test_parses_group_similarity(self):
        assert _parse_clamp3_score(_SAMPLE_OUTPUT) == pytest.approx(0.7423)

    def test_returns_none_when_not_found(self):
        assert _parse_clamp3_score("No score here") is None

    def test_returns_none_for_empty_string(self):
        assert _parse_clamp3_score("") is None


class TestSaveResults:
    def test_label_appears_in_output(self, tmp_path):
        results = {"classical/angry": _SAMPLE_OUTPUT}
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file)
        content = out_file.read_text(encoding="utf-8")
        assert "classical/angry" in content

    def test_score_is_formatted(self, tmp_path):
        results = {"classical/angry": _SAMPLE_OUTPUT}
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file)
        content = out_file.read_text(encoding="utf-8")
        assert "0.7423" in content

    def test_file_counts_appear(self, tmp_path):
        results = {"jazz/happy": _SAMPLE_OUTPUT}
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file)
        content = out_file.read_text(encoding="utf-8")
        assert "10 gen" in content
        assert "100 ref" in content

    def test_title_appears_in_header(self, tmp_path):
        results = {"classical": _SAMPLE_OUTPUT}
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file, title="per gatunek")
        content = out_file.read_text(encoding="utf-8")
        assert "per gatunek" in content

    def test_summary_stats_written_for_multiple_results(self, tmp_path):
        results = {
            "jazz": "Group similarity: 0.8\nTotal query features: 5\nTotal reference features: 50\n",
            "rock": "Group similarity: 0.6\nTotal query features: 3\nTotal reference features: 30\n",
        }
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file)
        content = out_file.read_text(encoding="utf-8")
        assert "Srednia" in content
        assert "Min" in content
        assert "Maks" in content

    def test_multiple_labels_appear(self, tmp_path):
        results = {"jazz/happy": _SAMPLE_OUTPUT, "rock/sad": _SAMPLE_OUTPUT}
        out_file = tmp_path / "results.txt"
        _save_results(results, out_file)
        content = out_file.read_text(encoding="utf-8")
        assert "jazz/happy" in content
        assert "rock/sad" in content


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