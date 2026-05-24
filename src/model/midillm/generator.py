"""Low-level wrapper around the MIDI-LLM ``generate_transformers.py`` script."""

import subprocess
import sys
from pathlib import Path


class MidiLLMGenerator:
    """Wrapper that invokes the MIDI-LLM generation script as a subprocess.

    Args:
        script_path: Path to ``generate_transformers.py``.
        python_executable: Python interpreter to use (should point to the
            ``midi-llm`` conda environment).
    """

    def __init__(self, script_path: Path, python_executable: str = sys.executable):
        self.script_path = script_path
        self.python = python_executable

    def generate_batch(self, prompts_file: Path, output_root: Path, n_outputs: int = 1) -> None:
        """Generate MIDI files from a prompts file.

        Args:
            prompts_file: Text file with one prompt per line.
            output_root: Root directory for generator output.  The script
                creates timestamped sub-directories inside this path.
            n_outputs: Number of MIDI files to generate per prompt line.
        """
        output_root.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.python,
            str(self.script_path.resolve()),
            "--prompts_file",
            str(prompts_file.resolve()),
            "--output_root",
            str(output_root.resolve()),
            "--n_outputs",
            str(n_outputs),
            "--no-synthesize",
        ]

        subprocess.run(cmd, check=True, cwd=self.script_path.parent)
