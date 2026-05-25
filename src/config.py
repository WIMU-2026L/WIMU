"""Project-wide configuration loaded from config.yaml at the repository root."""

from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_FILE = _ROOT / "config.yaml"

with open(_CONFIG_FILE, encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f)

_paths = _cfg["paths"]
_midillm = _cfg["models"]["midillm"]
_clamp3 = _cfg["models"]["clamp3"]
_musecoco = _cfg["models"]["musecoco"]
_wandb = _cfg.get("wandb", {})

# ---------------------------------------------------------------------------
# Dataset paths
# ---------------------------------------------------------------------------
XMIDI_URL: str = _paths["xmidi_url"]
XMIDI_DIR: Path = _ROOT / _paths["xmidi_data_dir"]
XMIDI_DATA_DIR: Path = _ROOT / _paths["xmidi_data_dir"]
XMIDI_SUBSET_DIR: Path = _ROOT / _paths["xmidi_subset_dir"]
XMIDI_GENERATED_DIR: Path = _ROOT / _paths["xmidi_generated_dir"]
XMIDI_ORGANIZED_DIR: Path = _ROOT / _paths["xmidi_organized_dir"]
XMIDI_ZIP_PATH: Path = XMIDI_DIR / "xmidi.zip"

GENERATED_DIR: Path = _ROOT / _paths["generated_dir"]
PROMPTS_DIR: Path = _ROOT / _paths["prompts_dir"]
PROMPTS_JSON: Path = _ROOT / _paths["prompts_json"]
RESULTS_DIR: Path = _ROOT / _paths["results_dir"]
LOGS_DIR: Path = _ROOT / _paths["logs_dir"]

# ---------------------------------------------------------------------------
# Model paths
# ---------------------------------------------------------------------------
MIDILLM_SCRIPT: Path = _ROOT / _midillm["script"]
MIDILLM_PYTHON: str = _midillm["python"]
MIDILLM_OUTPUT_DIR: Path = _ROOT / _midillm["output_dir"]

CLAMP3_PYTHON: str = _clamp3["python"]
CLAMP3_SCRIPT: Path = Path(_clamp3["script"])
CLAMP3_ENV_DIR: str = _clamp3["env_dir"]

MUSECOCO_OUTPUT_DIR: Path = _ROOT / _musecoco["output_dir"]
MUSECOCO_PYTHON: str = _musecoco["python"]
MUSECOCO_MIDI_SUBPATH: str = _musecoco["midi_subpath"]

# ---------------------------------------------------------------------------
# Weights & Biases
# ---------------------------------------------------------------------------
WANDB_PROJECT: str = _wandb.get("project", "wimu-music-eval")
WANDB_ENTITY: str | None = _wandb.get("entity")
