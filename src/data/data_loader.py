from pathlib import Path
import zipfile
import gdown
from data.infer_command import make_generated_midi_path
from data.midisample_class import MidiSample, load_midi_samples
from data.remi_converter import convert_remi_file_to_midi
from config import XMIDI_URL, XMIDI_ZIP_PATH, XMIDI_DIR, XMIDI_DATA_DIR

def load_data(data_dir: Path) -> list[MidiSample]:
    return load_midi_samples(data_dir)

def load_remi_data(data_dir: Path) -> list[Path]:
    return sorted(data_dir.glob("*/remi/*.txt"))

def convert_remi_data(source_dir: Path, target_dir: Path) -> list[Path]:
    converted_files = []

    for remi_file in load_remi_data(source_dir):
        infer_command_path = remi_file.parent.parent / "infer_command.json"
        target_path = make_generated_midi_path(infer_command_path, remi_file, target_dir)
        converted_files.append(convert_remi_file_to_midi(remi_file, target_path))

    return converted_files

def download_and_extract():
    if XMIDI_DATA_DIR.exists() and any(XMIDI_DATA_DIR.glob("*.midi")):
        print("Dataset already available.")
        return

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
