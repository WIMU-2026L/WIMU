from pathlib import Path
import json
import subprocess
import sys

class MidiLLMGenerator:
    def __init__(self, script_path: Path, python_executable: str = sys.executable):
        self.script_path = script_path
        self.python = python_executable

    def generate_batch(self, prompts_file: Path, output_root: Path, n_outputs: int = 1):
        output_root.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.python,
            str(self.script_path.resolve()),
            "--prompts_file", str(prompts_file.resolve()),
            "--output_root", str(output_root.resolve()),
            "--n_outputs", str(n_outputs),
            "--no-synthesize",
        ]

        subprocess.run(cmd, check=True, cwd=self.script_path.parent)