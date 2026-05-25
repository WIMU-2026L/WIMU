"""MIDI-LLM generation pipeline.

Reads prompts from per-genre/vibe ``.txt`` files and generates MIDI files
using the MIDI-LLM model via :class:`MidiLLMGenerator`.
"""

import json
import shutil
from pathlib import Path
import subprocess
import os
from config import MIDILLM_OUTPUT_DIR, MIDILLM_PYTHON, MIDILLM_SCRIPT, PROMPTS_DIR, PROMPTS_JSON, MUSECOCO_PYTHON
from model.midillm.generator import MidiLLMGenerator


def collect_generated_midis(raw_output_dir: Path, target_dir: Path) -> None:
    """Move generated ``.mid`` files from timestamped sub-directories to *target_dir*.

    The MIDI-LLM script creates one sub-directory per generation run.  This
    function flattens that structure into a single flat directory.

    Args:
        raw_output_dir: Temporary directory created by the generator.
        target_dir: Final destination for all ``.mid`` files.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    for mid_file in raw_output_dir.rglob("*.mid"):
        dest = target_dir / mid_file.name
        shutil.move(str(mid_file), str(dest))
    shutil.rmtree(raw_output_dir, ignore_errors=True)


def generate_midillm_samples(n_outputs: int = 1) -> None:
    """Generate MIDI samples for every (genre, vibe) pair using MIDI-LLM.

    Iterates over all entries in ``all_prompts.json`` and looks for a
    matching ``{genre}_{vibe}.txt`` prompt file.  For each pair the generator
    is called with *n_outputs* outputs per prompt line.

    Generated files are moved from the temporary ``_tmp/`` directory into
    ``data/generated/midi-llm/{genre}/{vibe}/``.

    Args:
        n_outputs: Number of MIDI files to generate per prompt line.
    """
    generator = MidiLLMGenerator(MIDILLM_SCRIPT, python_executable=MIDILLM_PYTHON)

    with open(PROMPTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    for genre, moods in data.items():
        for mood in moods:
            prompts_file = PROMPTS_DIR / f"{genre}_{mood}.txt"
            with open(prompts_file, 'w') as fp:
                prompts = [ d['text'] + "\n" for d in data[genre][mood] ]
                fp.writelines(prompts)

            if not prompts_file.exists():
                print(f"Brak pliku promptow: {prompts_file}, pomijam.")
                continue

            print(f"Generuje: {genre}/{mood} ({n_outputs} utwor/ow na prompt)...")

            raw_output = MIDILLM_OUTPUT_DIR / "_tmp" / f"{genre}_{mood}"
            generator.generate_batch(prompts_file, raw_output, n_outputs=n_outputs)

            target = MIDILLM_OUTPUT_DIR / genre / mood
            collect_generated_midis(raw_output, target)

            print(f"  -> zapisano do {target}")


def generate_musecoco_samples(n_outputs: int = 2) -> None:
    
    
    if MUSECOCO_PYTHON == "":
        raise Exception("Musecoco python path not defined.")
    custom_env = os.environ.copy()
    
    
    path = Path(MUSECOCO_PYTHON)
    custom_env["PATH"] = f"{path.parent}{os.pathsep}{custom_env.get('PATH', '')}"
    # print(custom_env["PATH"])
    subprocess.call('external/muzic/musecoco/1-text2attribute_model/predict.sh', shell=True, env=custom_env )
    subprocess.call(f'external/muzic/musecoco/2-attribute2music_model/interactive_1billion.sh 0 {n_outputs}', shell=True, env=custom_env, executable="/bin/bash")

if __name__ == "__main__":
    generate_midillm_samples()
