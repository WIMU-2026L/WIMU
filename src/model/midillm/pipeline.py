import json
import shutil
from pathlib import Path
from model.midillm.generator import MidiLLMGenerator

MIDILLM_SCRIPT = Path("external/MIDI-LLM/generate_transformers.py")
OUTPUT_DIR = Path("data/generated/midi-llm")
PROMPTS_DIR = Path("data/prompts")
PROMPTS_JSON = Path("data/prompts/all_prompts.json")
PYTHON = r"C:\Users\oskar\.conda\envs\midi-llm\python.exe"


def collect_generated_midis(raw_output_dir: Path, target_dir: Path):
    """Przenosi wygenerowane .mid z timestampowych folderów do target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for mid_file in raw_output_dir.rglob("*.mid"):
        dest = target_dir / mid_file.name
        shutil.move(str(mid_file), str(dest))
    shutil.rmtree(raw_output_dir, ignore_errors=True)


def generate_samples(n_outputs: int = 1):
    generator = MidiLLMGenerator(MIDILLM_SCRIPT, python_executable=PYTHON)

    with open(PROMPTS_JSON, "r") as f:
        data = json.load(f)

    for genre, moods in data.items():
        for mood in moods:
            prompts_file = PROMPTS_DIR / f"{genre}_{mood}.txt"
            if not prompts_file.exists():
                print(f"Brak pliku promptów: {prompts_file}, pomijam.")
                continue

            print(f"Generuję: {genre}/{mood} ({n_outputs} utwór/ów na prompt)...")

            raw_output = OUTPUT_DIR / "_tmp" / f"{genre}_{mood}"
            generator.generate_batch(prompts_file, raw_output, n_outputs=n_outputs)

            target = OUTPUT_DIR / genre / mood
            collect_generated_midis(raw_output, target)

            print(f"  -> zapisano do {target}")


if __name__ == "__main__":
    generate_samples()