from pathlib import Path
import zipfile
import gdown
from src.data.midisample_class import MidiSample, load_midi_samples
from src.config import XMIDI_URL, XMIDI_ZIP_PATH, XMIDI_DIR

def load_data(data_dir: Path) -> list[MidiSample]:
    return load_midi_samples(data_dir)

def download_and_extract():

    XMIDI_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading dataset...")
    gdown.download(XMIDI_URL, str(XMIDI_ZIP_PATH), quiet=False)

    print("Extracting...")
    try:
        with zipfile.ZipFile(XMIDI_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(XMIDI_DIR)
    finally:
        if XMIDI_ZIP_PATH.exists():
            XMIDI_ZIP_PATH.unlink()
    
    print("Done!")
