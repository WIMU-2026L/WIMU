from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
XMIDI_DIR = DATA_DIR
SOURCE_DIR = BASE_DIR / "src"
LOGS_DIR = SOURCE_DIR / "logs"
RESULTS_DIR = BASE_DIR / "results"
PROMPTS_DIR = DATA_DIR / "prompts"
GENERATED_DIR = DATA_DIR / "generated"

XMIDI_URL = "https://drive.google.com/uc?id=1qDkSH31x7jN8X-2RyzB9wuxGji4QxYyA"
XMIDI_ZIP_PATH = XMIDI_DIR / "xmidi.zip"
XMIDI_DATA_DIR = XMIDI_DIR / "XMIDI_Dataset"
XMIDI_SUBSET_DIR = XMIDI_DIR / "XMIDI_subset"
XMIDI_GENERATED_DIR = XMIDI_DIR / "XMIDI_generated_music"
XMIDI_ORGANIZED_DIR = DATA_DIR / "XMIDI_Organized"
MIDILLM_GENERATED_DIR = GENERATED_DIR / "midi-llm"
MUSECOCO_GENERATED_DIR = GENERATED_DIR / "musecoco"
