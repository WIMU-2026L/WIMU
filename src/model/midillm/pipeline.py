import os
import shutil
import sys
from pathlib import Path
from model.midillm.generator import MidiLLMGenerator

MIDILLM_SCRIPT = Path("external/midi-llm/generate_transformers.py")
OUTPUT_DIR = Path("data/generated/midi-llm")
PROMPTS_DIR = Path("data/prompts")
PYTHON = os.environ.get("MIDILLM_PYTHON", sys.executable)


def collect_generated_midis(raw_output_dir: Path, target_dir: Path):
    """Przenosi wygenerowane .mid z timestampowych folderów do target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for mid_file in raw_output_dir.rglob("*.mid"):
        dest = target_dir / mid_file.name
        shutil.move(str(mid_file), str(dest))
    shutil.rmtree(raw_output_dir, ignore_errors=True)


def generate_samples(n_outputs: int = 1):
    if not MIDILLM_SCRIPT.exists():
        raise FileNotFoundError(
            "MIDI-LLM generator script was not found at "
            f"{MIDILLM_SCRIPT}. Initialize submodules first with "
            "'git submodule update --init --recursive'."
        )

    prompt_files = sorted(PROMPTS_DIR.glob("*.txt"))
    if not prompt_files:
        raise FileNotFoundError(
            f"No prompt files found in {PROMPTS_DIR}. Run prompt preparation first."
        )

    generator = MidiLLMGenerator(MIDILLM_SCRIPT, python_executable=PYTHON)
    generated_count = 0

    for prompts_file in prompt_files:
        if prompts_file.name == "prompt_example.txt":
            continue

        try:
            genre, mood = prompts_file.stem.split("_", maxsplit=1)
        except ValueError as exc:
            raise ValueError(
                f"Prompt file {prompts_file} does not match the expected <genre>_<mood>.txt format."
            ) from exc

        print(f"Generuję: {genre}/{mood} ({n_outputs} utwór/ów na prompt)...")

        raw_output = OUTPUT_DIR / "_tmp" / f"{genre}_{mood}"
        generator.generate_batch(prompts_file, raw_output, n_outputs=n_outputs)

        target = OUTPUT_DIR / genre / mood
        collect_generated_midis(raw_output, target)
        generated_count += 1

        print(f"  -> zapisano do {target}")

    if generated_count == 0:
        raise RuntimeError(
            f"No usable prompt files were found in {PROMPTS_DIR}. Nothing was generated."
        )


if __name__ == "__main__":
    generate_samples()
