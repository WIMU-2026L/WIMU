"""Unit tests for prompts JSON loading and prompt file parsing."""

import json

import pytest

from data.midisample_class import MidiSample, make_midi_sample


class TestPromptsJson:
    def test_valid_json_structure(self, tmp_path):
        data = {
            "classical": {
                "angry": [{"text": "An angry classical piece."}],
                "happy": [{"text": "A happy classical piece."}],
            }
        }
        json_file = tmp_path / "all_prompts.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        with open(json_file, encoding="utf-8") as f:
            loaded = json.load(f)

        assert "classical" in loaded
        assert "angry" in loaded["classical"]
        assert loaded["classical"]["angry"][0]["text"] == "An angry classical piece."

    def test_prompt_text_is_non_empty(self, tmp_path):
        data = {
            "jazz": {
                "sad": [
                    {"text": "A sad jazz piece."},
                    {"text": "Another sad jazz piece."},
                ]
            }
        }
        json_file = tmp_path / "prompts.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        with open(json_file, encoding="utf-8") as f:
            loaded = json.load(f)

        for entry in loaded["jazz"]["sad"]:
            assert entry["text"].strip() != ""

    def test_prompt_file_lines_match_json_entries(self, tmp_path):
        entries = [{"text": "Prompt one."}, {"text": "Prompt two."}, {"text": "Prompt three."}]
        data = {"rock": {"angry": entries}}
        json_file = tmp_path / "prompts.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        prompts_txt = tmp_path / "rock_angry.txt"
        prompts_txt.write_text(
            "\n".join(e["text"].strip().replace("\n", " ") for e in entries),
            encoding="utf-8",
        )

        lines = prompts_txt.read_text(encoding="utf-8").splitlines()
        assert len(lines) == len(entries)


class TestMakeMidiSample:
    def test_parses_valid_filename(self, tmp_path):
        f = tmp_path / "XMIDI_angry_classical_001.midi"
        f.write_bytes(b"")

        sample = make_midi_sample(f)

        assert isinstance(sample, MidiSample)
        assert sample.genre == "classical"
        assert sample.vibe == "angry"
        assert sample.id == "001"

    def test_raises_on_invalid_filename(self, tmp_path):
        f = tmp_path / "invalid.midi"
        f.write_bytes(b"")

        with pytest.raises((ValueError, TypeError)):
            make_midi_sample(f)
