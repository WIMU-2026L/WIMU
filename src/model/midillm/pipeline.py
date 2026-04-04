from pathlib import Path
from model.midillm.generator import MidiLLMGenerator

MIDILLM_SCRIPT = Path("external/midi-llm/infer.py")
OUTPUT_DIR = Path("data/generated/midi-llm")

GENRES = ["jazz", "rock", "classical"]
N_SAMPLES = 5


def generate_samples():
    generator = MidiLLMGenerator(MIDILLM_SCRIPT)

    for genre in GENRES:
        for i in range(N_SAMPLES):
            prompt = f"Generate a {genre} piano piece"

            output_path = OUTPUT_DIR / f"{genre}_{i}.mid"

            print(f"Generating {output_path}...")
            generator.generate(prompt, output_path)
