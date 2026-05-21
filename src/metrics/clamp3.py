import os
import subprocess
from pathlib import Path
import shutil
import tempfile

CLAMP3_PYTHON = r"C:\Users\oskar\.conda\envs\clamp3\python.exe"
CLAMP3_SCRIPT = Path(r"D:\GitHub\WIMU\external\clamp3\clamp3_score.py")
CLAMP3_ENV_DIR = r"C:\Users\oskar\.conda\envs\clamp3"


def evaluate_with_clamp3(generated_dir: Path, reference_dir: Path, results_dir: Path):
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "xmidi_midillm_clamp3_results.txt"
    cache_dir = CLAMP3_SCRIPT.parent / "cache"
    results = {}

    # Ustaw PATH tak żeby "python" wskazywało na conda
    env = os.environ.copy()
    env["PATH"] = CLAMP3_ENV_DIR + os.pathsep + str(Path(CLAMP3_ENV_DIR) / "Scripts") + os.pathsep + env["PATH"]

    for gen_genre_dir in generated_dir.iterdir():
        genre = gen_genre_dir.name

        for gen_vibe_dir in gen_genre_dir.iterdir():
            vibe = gen_vibe_dir.name
            ref_dir = reference_dir / genre / vibe

            if not ref_dir.exists():
                print(f"Brak referencji dla {genre}/{vibe}, pomijam.")
                continue

            # Unikalne nazwy folderów tymczasowych z genre w nazwie
            tmp_gen = CLAMP3_SCRIPT.parent / f"_eval_gen_{genre}_{vibe}"
            tmp_ref = CLAMP3_SCRIPT.parent / f"_eval_ref_{genre}_{vibe}"

            # Wyczyść i skopiuj
            for d in [tmp_gen, tmp_ref]:
                if d.exists():
                    shutil.rmtree(d)

            shutil.copytree(gen_vibe_dir, tmp_gen)
            shutil.copytree(ref_dir, tmp_ref)

            # Wyczyść cache przed każdym wywołaniem
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            cache_dir.mkdir()

            print(f"Porównuję: {genre}/{vibe}...")

            result = subprocess.run(
                [
                    CLAMP3_PYTHON,
                    str(CLAMP3_SCRIPT.resolve()),
                    str(tmp_gen.resolve()),
                    str(tmp_ref.resolve()),
                    "--group",
                ],
                capture_output=True,
                text=True,
                cwd=CLAMP3_SCRIPT.parent.resolve(),
                env=env,  # przekaż zmodyfikowany PATH
            )

            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

            if result.returncode != 0:
                print(f"Błąd dla {genre}/{vibe}:\n{result.stderr}")

            results[f"{genre}/{vibe}"] = result.stdout

            # Posprzątaj tymczasowe foldery
            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)

            print(result.stdout)
            results[f"{genre}/{vibe}"] = result.stdout

    with open(results_file, "w", encoding="utf-8") as f:
        for key, output in results.items():
            f.write(f"=== {key} ===\n")
            f.write(output + "\n")

    print(f"Wyniki zapisane do {results_file}")