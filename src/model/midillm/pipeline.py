import json
import shutil
from pathlib import Path
from model.midillm.generator import MidiLLMGenerator

MIDILLM_SCRIPT = Path("external/MIDI-LLM/generate_transformers.py")
OUTPUT_DIR = Path("data/generated/midi-llm")
PROMPTS_DIR = Path("data/prompts")
PROMPTS_JSON = Path("data/prompts/all_prompts.json")
PYTHON = r"C:\Users\oskar\.conda\envs\midi-llm\python.exe"


def build_prompts_file(genre: str, mood: str, entries: list) -> Path:
    prompts = [e["text"].strip().replace("\n", " ") for e in entries]

    prompts_file = PROMPTS_DIR / f"{genre}_{mood}.txt"
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(prompts_file, "w") as f:
        f.write("\n".join(prompts))

    return prompts_file


def collect_generated_midis(raw_output_dir: Path, target_dir: Path):
    """Przenosi wygenerowane .mid z timestampowych folderów do target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for mid_file in raw_output_dir.rglob("*.mid"):
        dest = target_dir / mid_file.name
        shutil.move(str(mid_file), str(dest))
    # Usuń puste foldery po przeniesieniu
    shutil.rmtree(raw_output_dir, ignore_errors=True)


def generate_samples():
    generator = MidiLLMGenerator(MIDILLM_SCRIPT, python_executable=PYTHON)

    with open(PROMPTS_JSON, "r") as f:
        data = json.load(f)

    for genre, moods in data.items():
        for mood, entries in moods.items():
            print(f"Generuję: {genre}/{mood} ({len(entries)} promptów)...")

            prompts_file = build_prompts_file(genre, mood, entries)

            # Tymczasowy folder dla tej pary genre/mood
            raw_output = OUTPUT_DIR / "_tmp" / f"{genre}_{mood}"
            generator.generate_batch(prompts_file, raw_output)

            # Przenieś do docelowej struktury
            target = OUTPUT_DIR / genre / mood
            collect_generated_midis(raw_output, target)

            print(f"  -> zapisano do {target}")


if __name__ == "__main__":
    generate_samples()