from pathlib import Path
import subprocess


class MidiLLMGenerator:
    def __init__(self, script_path: Path):
        self.script_path = script_path

    def generate(self, prompt: str, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "python",
            str(self.script_path),
            "--prompt", prompt,
            "--output", str(output_path)
        ]

        subprocess.run(cmd, check=True)