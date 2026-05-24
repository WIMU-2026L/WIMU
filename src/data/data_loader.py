"""Dataset download and loading utilities."""

import zipfile
from pathlib import Path

import gdown

from config import XMIDI_DIR, XMIDI_URL, XMIDI_ZIP_PATH
from data.midisample_class import MidiSample, load_midi_samples


def load_data(data_dir: Path) -> list[MidiSample]:
    """Load all MIDI samples from *data_dir*.

    Args:
        data_dir: Directory containing ``.midi`` files in XMIDI naming format.

    Returns:
        List of :class:`~data.midisample_class.MidiSample` objects.
    """
    return load_midi_samples(data_dir)


def download_and_extract() -> None:
    """Download the XMIDI dataset from Google Drive and extract it.

    The zip file is removed after successful extraction.  The destination
    directory is taken from :data:`config.XMIDI_DIR`.
    """
    XMIDI_DIR.mkdir(parents=True, exist_ok=True)

    print("Pobieranie datasetu...")
    gdown.download(XMIDI_URL, str(XMIDI_ZIP_PATH), quiet=False)

    print("Rozpakowywanie...")
    try:
        with zipfile.ZipFile(XMIDI_ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(XMIDI_DIR)
    finally:
        if XMIDI_ZIP_PATH.exists():
            XMIDI_ZIP_PATH.unlink()

    print("Gotowe!")
