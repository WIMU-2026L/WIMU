import os
import subprocess
from pathlib import Path
import shutil

CLAMP3_PYTHON = r"C:\Users\oskar\.conda\envs\clamp3\python.exe"
CLAMP3_SCRIPT = Path(r"D:\GitHub\WIMU\external\clamp3\clamp3_score.py")
CLAMP3_ENV_DIR = r"C:\Users\oskar\.conda\envs\clamp3"

_MIDI_EXTS = {".mid", ".midi"}


def _make_env() -> dict:
    env = os.environ.copy()
    env["PATH"] = CLAMP3_ENV_DIR + os.pathsep + str(Path(CLAMP3_ENV_DIR) / "Scripts") + os.pathsep + env["PATH"]
    return env


def _copy_midi_files(src_dir: Path, dst_dir: Path, prefix: str = "") -> int:
    count = 0
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix.lower() in _MIDI_EXTS:
            dst_name = f"{prefix}{f.name}" if prefix else f.name
            shutil.copy2(f, dst_dir / dst_name)
            count += 1
    return count


def _run_clamp3(tmp_gen: Path, tmp_ref: Path, label: str, env: dict) -> str:
    cache_dir = CLAMP3_SCRIPT.parent / "cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir()

    print(f"Porównuję: {label}...")
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
        env=env,
    )
    print(f"stdout: {result.stdout}")
    if result.returncode != 0:
        print(f"stderr: {result.stderr}")
    return result.stdout


def _save_results(results: dict, results_file: Path, section_suffix: str = ""):
    with open(results_file, "w", encoding="utf-8") as f:
        for key, output in results.items():
            label = f"{key}{' ' + section_suffix if section_suffix else ''}"
            f.write(f"=== {label} ===\n")
            f.write(output + "\n")
    print(f"Wyniki zapisane do {results_file}")


# ---------------------------------------------------------------------------
# Istniejące porównanie: genre/vibe z xmidi vs genre/vibe z modelu
# ---------------------------------------------------------------------------

def evaluate_with_clamp3(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_results.txt",
    midi_subpath: str = None,
):
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / results_filename
    env = _make_env()
    results = {}

    for gen_genre_dir in generated_dir.iterdir():
        if not gen_genre_dir.is_dir() or gen_genre_dir.name.startswith("_"):
            continue
        genre = gen_genre_dir.name

        for gen_vibe_dir in gen_genre_dir.iterdir():
            if not gen_vibe_dir.is_dir():
                continue
            vibe = gen_vibe_dir.name

            actual_gen_dir = gen_vibe_dir / midi_subpath if midi_subpath else gen_vibe_dir
            if not actual_gen_dir.exists():
                print(f"Brak plików dla {genre}/{vibe} w {actual_gen_dir}, pomijam.")
                continue

            ref_dir = reference_dir / genre / vibe
            if not ref_dir.exists():
                print(f"Brak referencji dla {genre}/{vibe}, pomijam.")
                continue

            tmp_gen = CLAMP3_SCRIPT.parent / f"_eval_gen_{genre}_{vibe}"
            tmp_ref = CLAMP3_SCRIPT.parent / f"_eval_ref_{genre}_{vibe}"
            for d in [tmp_gen, tmp_ref]:
                if d.exists():
                    shutil.rmtree(d)

            shutil.copytree(actual_gen_dir, tmp_gen)
            shutil.copytree(ref_dir, tmp_ref)

            results[f"{genre}/{vibe}"] = _run_clamp3(tmp_gen, tmp_ref, f"{genre}/{vibe}", env)

            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)

    _save_results(results, results_file)


# ---------------------------------------------------------------------------
# Porównanie per gatunek: wszystkie viby łącznie
# ---------------------------------------------------------------------------

def evaluate_clamp3_by_genre(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_by_genre.txt",
    midi_subpath: str = None,
):
    """Porównuje wszystkie pliki danego gatunku (wszystkie viby razem) z referencją."""
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / results_filename
    env = _make_env()
    results = {}

    genres = sorted(
        d.name for d in reference_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )

    for genre in genres:
        gen_genre_dir = generated_dir / genre
        ref_genre_dir = reference_dir / genre
        if not gen_genre_dir.exists() or not ref_genre_dir.exists():
            print(f"Brak danych dla gatunku {genre}, pomijam.")
            continue

        tmp_gen = CLAMP3_SCRIPT.parent / f"_eval_gen_{genre}_allvibes"
        tmp_ref = CLAMP3_SCRIPT.parent / f"_eval_ref_{genre}_allvibes"
        for d in [tmp_gen, tmp_ref]:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir()

        for vibe_dir in gen_genre_dir.iterdir():
            if not vibe_dir.is_dir() or vibe_dir.name.startswith("_"):
                continue
            actual_vibe_dir = vibe_dir / midi_subpath if midi_subpath else vibe_dir
            if actual_vibe_dir.exists():
                _copy_midi_files(actual_vibe_dir, tmp_gen, prefix=f"{vibe_dir.name}_")

        for vibe_dir in ref_genre_dir.iterdir():
            if not vibe_dir.is_dir() or vibe_dir.name.startswith("_"):
                continue
            if vibe_dir.exists():
                _copy_midi_files(vibe_dir, tmp_ref, prefix=f"{vibe_dir.name}_")

        if not any(tmp_gen.iterdir()) or not any(tmp_ref.iterdir()):
            print(f"Brak plików MIDI dla gatunku {genre}, pomijam.")
            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)
            continue

        results[genre] = _run_clamp3(tmp_gen, tmp_ref, f"{genre} (wszystkie viby)", env)

        shutil.rmtree(tmp_gen)
        shutil.rmtree(tmp_ref)

    _save_results(results, results_file, section_suffix="[wszystkie viby]")


# ---------------------------------------------------------------------------
# Porównanie per vibe: wszystkie gatunki łącznie
# ---------------------------------------------------------------------------

def evaluate_clamp3_by_vibe(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_by_vibe.txt",
    midi_subpath: str = None,
):
    """Porównuje wszystkie pliki danego vibu (wszystkie gatunki razem) z referencją."""
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / results_filename
    env = _make_env()
    results = {}

    # Zbierz wszystkie viby ze wszystkich gatunków w referencji
    vibes = sorted({
        vibe_dir.name
        for genre_dir in reference_dir.iterdir()
        if genre_dir.is_dir() and not genre_dir.name.startswith("_")
        for vibe_dir in genre_dir.iterdir()
        if vibe_dir.is_dir() and not vibe_dir.name.startswith("_")
    })

    for vibe in vibes:
        tmp_gen = CLAMP3_SCRIPT.parent / f"_eval_gen_{vibe}_allgenres"
        tmp_ref = CLAMP3_SCRIPT.parent / f"_eval_ref_{vibe}_allgenres"
        for d in [tmp_gen, tmp_ref]:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir()

        for genre_dir in generated_dir.iterdir():
            if not genre_dir.is_dir() or genre_dir.name.startswith("_"):
                continue
            actual_vibe_dir = genre_dir / vibe
            if midi_subpath:
                actual_vibe_dir = actual_vibe_dir / midi_subpath
            if actual_vibe_dir.exists():
                _copy_midi_files(actual_vibe_dir, tmp_gen, prefix=f"{genre_dir.name}_")

        for genre_dir in reference_dir.iterdir():
            if not genre_dir.is_dir() or genre_dir.name.startswith("_"):
                continue
            ref_vibe_dir = genre_dir / vibe
            if ref_vibe_dir.exists():
                _copy_midi_files(ref_vibe_dir, tmp_ref, prefix=f"{genre_dir.name}_")

        if not any(tmp_gen.iterdir()) or not any(tmp_ref.iterdir()):
            print(f"Brak plików MIDI dla vibu {vibe}, pomijam.")
            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)
            continue

        results[vibe] = _run_clamp3(tmp_gen, tmp_ref, f"{vibe} (wszystkie gatunki)", env)

        shutil.rmtree(tmp_gen)
        shutil.rmtree(tmp_ref)

    _save_results(results, results_file, section_suffix="[wszystkie gatunki]")


# ---------------------------------------------------------------------------
# Wrapper: wszystkie trzy porównania naraz
# ---------------------------------------------------------------------------

def evaluate_all_clamp3(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    model_name: str = "model",
    midi_subpath: str = None,
):
    """
    Uruchamia wszystkie trzy warianty porównania CLaMP3:
      1. genre/vibe  – szczegółowe porównanie par (gatunek, vib)
      2. by_genre    – wszystkie viby danego gatunku łącznie
      3. by_vibe     – wszystkie gatunki danego vibu łącznie
    """
    print(f"\n{'='*60}")
    print(f"CLaMP3: porównanie szczegółowe (genre/vibe) — {model_name}")
    print(f"{'='*60}")
    evaluate_with_clamp3(
        generated_dir, reference_dir, results_dir,
        results_filename=f"{model_name}_genre_vibe_clamp3.txt",
        midi_subpath=midi_subpath,
    )

    print(f"\n{'='*60}")
    print(f"CLaMP3: per gatunek (wszystkie viby razem) — {model_name}")
    print(f"{'='*60}")
    evaluate_clamp3_by_genre(
        generated_dir, reference_dir, results_dir,
        results_filename=f"{model_name}_by_genre_clamp3.txt",
        midi_subpath=midi_subpath,
    )

    print(f"\n{'='*60}")
    print(f"CLaMP3: per vibe (wszystkie gatunki razem) — {model_name}")
    print(f"{'='*60}")
    evaluate_clamp3_by_vibe(
        generated_dir, reference_dir, results_dir,
        results_filename=f"{model_name}_by_vibe_clamp3.txt",
        midi_subpath=midi_subpath,
    )
