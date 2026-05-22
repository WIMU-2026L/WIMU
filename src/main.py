from pathlib import Path
from data.dataset_processing import organize_midi_files
import data.data_loader as data_loader
from data.midisample_class import MidiSample
from config import XMIDI_DATA_DIR
from model.midillm.pipeline import generate_samples

from config import XMIDI_DATA_DIR, XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR, LOGS_DIR
# from metrics.fmd import calculate_fmd,calculate_fmd_inf
import logging

from metrics.clamp3 import evaluate_with_clamp3
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Sample generation
    # data_loader.download_and_extract()
    # midi_samples: list[MidiSample] = data_loader.load_data(XMIDI_DATA_DIR)
    # print(f"Loaded {len(midi_samples)} MIDI samples.")

    # Generacja próbek muzycznych za pomocą modelu MIDILLM
    # generate_samples()

    # XMIDI_DIR = Path("D:\\GitHub\\WIMU\\data\\XMIDI_Dataset")       # folder z wszystkimi plikami
    # OUTPUT_DIR = Path("D:\\GitHub\\WIMU\\data\\XMIDI_Organized") # docelowa struktura

    # organize_midi_files(XMIDI_DIR, OUTPUT_DIR)

    GENERATED_DIR = Path(r"D:\GitHub\WIMU\data\generated\\musecoco")
    REFERENCE_DIR = Path(r"D:\GitHub\WIMU\data\XMIDI_Organized")
    RESULTS_DIR   = Path(r"D:\GitHub\WIMU\results")
    # evaluate_with_clamp3(GENERATED_DIR, REFERENCE_DIR, RESULTS_DIR)

    evaluate_with_clamp3(
        generated_dir=Path(r"D:\GitHub\WIMU\data\generated\musecoco"),
        reference_dir=REFERENCE_DIR,
        results_dir=RESULTS_DIR,
        results_filename="xmidi_musecoco_clamp3_results.txt",
        midi_subpath="topk15-t0.7-ngram16/0/midi",
    )
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
