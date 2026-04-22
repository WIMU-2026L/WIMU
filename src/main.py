import data.data_loader as data_loader
from data.midisample_class import MidiSample
from config import XMIDI_DATA_DIR
from model.midillm.pipeline import generate_samples

from config import XMIDI_DATA_DIR, XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR, LOGS_DIR
# from metrics.fmd import calculate_fmd,calculate_fmd_inf
import logging
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Sample generation
    # data_loader.download_and_extract()
    # midi_samples: list[MidiSample] = data_loader.load_data(XMIDI_DATA_DIR)
    # print(f"Loaded {len(midi_samples)} MIDI samples.")
    generate_samples()

     # MIDILLM
    # logging.basicConfig(filename=LOGS_DIR / "app.log", level=logging.INFO)

    # data_loader.download_and_extract()
    # midi_samples: list[MidiSample] = data_loader.load_data(XMIDI_DATA_DIR)
    # print(f"Loaded {len(midi_samples)} MIDI samples.")

    # midi_subset: list[MidiSample] = data_loader.load_data(XMIDI_SUBSET_DIR)
    # generated_music: list[MidiSample] = data_loader.load_data(XMIDI_GENERATED_DIR)

    # fmd_score = calculate_fmd(XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR)
    # logger.info(f"fmd_score : {fmd_score}")
    # fmd_score_inf = calculate_fmd_inf(XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR)
    # logger.info(f"fmd_score_inf:{fmd_score_inf}")
