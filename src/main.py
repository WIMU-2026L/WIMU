import data.data_loader as data_loader
from data.midisample_class import MidiSample
from config import XMIDI_DATA_DIR

if __name__ == "__main__":
    data_loader.download_and_extract()
    midi_samples: list[MidiSample] = data_loader.load_data(XMIDI_DATA_DIR)
    print(f"Loaded {len(midi_samples)} MIDI samples.")