"""Data model for a single XMIDI sample."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MidiSample:
    """Represents one MIDI file from the XMIDI dataset.

    Attributes:
        file_path: Absolute path to the ``.midi`` file.
        genre: Musical genre label (e.g. ``"classical"``).
        vibe: Emotional vibe label (e.g. ``"angry"``).
        id: Unique sample identifier extracted from the filename.
    """

    file_path: Path
    genre: str
    vibe: str
    id: str


def make_midi_sample(file_path: Path) -> MidiSample:
    """Parse an XMIDI filename and construct a :class:`MidiSample`.

    Expects filenames in the format ``XMIDI_{vibe}_{genre}_{id}.midi``.

    Args:
        file_path: Path to the MIDI file.

    Returns:
        Populated :class:`MidiSample` instance.

    Raises:
        ValueError: If the filename does not follow the expected format.
    """
    midi_file_name = file_path.stem
    _, vibe, genre, id_ = midi_file_name.split("_")
    return MidiSample(file_path=file_path, genre=genre, vibe=vibe, id=id_)


def load_midi_samples(data_dir: Path) -> list[MidiSample]:
    """Load all XMIDI samples from *data_dir*.

    Args:
        data_dir: Directory containing ``.midi`` files named in the XMIDI
            convention.

    Returns:
        List of :class:`MidiSample` objects, one per file found.
    """
    return [make_midi_sample(f) for f in data_dir.glob("*.midi")]
