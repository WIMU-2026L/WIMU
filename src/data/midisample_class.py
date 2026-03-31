from dataclasses import dataclass
from pathlib import Path

@dataclass
class MidiSample:
    file_path: Path
    genre: str
    vibe: str
    id: str

def make_midi_sample(file_path: Path) -> MidiSample:
    midi_file_name = file_path.stem
    _, vibe, genre, id_ = midi_file_name.split("_")
    return MidiSample(file_path=file_path, genre=genre, vibe=vibe, id=id_)

def load_midi_samples(data_dir: Path) -> list[MidiSample]:
    midi_samples = []
    for midi_file in data_dir.glob('*.midi'):
        midi_samples.append(make_midi_sample(midi_file))
    return midi_samples