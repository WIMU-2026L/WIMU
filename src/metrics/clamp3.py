"""CLaMP3-based evaluation of generated MIDI against a reference dataset.

Three comparison modes are provided:
- per genre/vibe pair   (existing fine-grained comparison)
- aggregated by genre   (all vibes pooled per genre)
- aggregated by vibe    (all genres pooled per vibe)
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from config import CLAMP3_ENV_DIR, CLAMP3_PYTHON, CLAMP3_SCRIPT

_MIDI_EXTS = {".mid", ".midi"}


def _make_env() -> dict:
    """Build an environment dict that puts the CLaMP3 conda env first on PATH."""
    env = os.environ.copy()
    env["PATH"] = (
        CLAMP3_ENV_DIR
        + os.pathsep
        + str(Path(CLAMP3_ENV_DIR) / "Scripts")
        + os.pathsep
        + env["PATH"]
    )
    return env


def _copy_midi_files(src_dir: Path, dst_dir: Path, prefix: str = "") -> int:
    """Copy all MIDI files from *src_dir* to *dst_dir* with an optional filename prefix.

    Args:
        src_dir: Directory to copy files from.
        dst_dir: Destination directory (must already exist).
        prefix: String prepended to each filename to avoid collisions.

    Returns:
        Number of files copied.
    """
    count = 0
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix.lower() in _MIDI_EXTS:
            dst_name = f"{prefix}{f.name}" if prefix else f.name
            shutil.copy2(f, dst_dir / dst_name)
            count += 1
    return count


def _run_clamp3(tmp_gen: Path, tmp_ref: Path, label: str, env: dict) -> str:
    """Run the CLaMP3 score script and return its stdout.

    Args:
        tmp_gen: Temporary directory with generated MIDI files.
        tmp_ref: Temporary directory with reference MIDI files.
        label: Human-readable label for progress logging.
        env: Environment variables dict (with CLaMP3 env on PATH).

    Returns:
        Raw stdout from the CLaMP3 script.
    """
    print(f"Porownuje: {label}...")
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


def _save_results(results: dict, results_file: Path, section_suffix: str = "") -> None:
    """Write a results dict to a text file.

    Args:
        results: Mapping of label to CLaMP3 output string.
        results_file: Path of the output file to write.
        section_suffix: Optional suffix appended to each section header.
    """
    with open(results_file, "w", encoding="utf-8") as f:
        for key, output in results.items():
            label = f"{key}{' ' + section_suffix if section_suffix else ''}"
            f.write(f"=== {label} ===\n")
            f.write(output + "\n")
    print(f"Wyniki zapisane do {results_file}")


# ---------------------------------------------------------------------------
# Genre/vibe pair comparison (original fine-grained evaluation)
# ---------------------------------------------------------------------------


def evaluate_with_clamp3(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_results.txt",
    midi_subpath: Optional[str] = None,
) -> dict:
    """Compare generated vs reference MIDI for every (genre, vibe) pair.

    Args:
        generated_dir: Root of generated MIDI files, structured as
            ``genre/vibe/[midi_subpath]/``.
        reference_dir: Root of reference MIDI files, structured as
            ``genre/vibe/``.
        results_dir: Directory where the results text file is written.
        results_filename: Name of the output file.
        midi_subpath: Optional sub-path appended to each generated vibe
            directory (e.g. ``"topk15-t0.7-ngram16/0/midi"`` for MuseCoco).

    Returns:
        Dict mapping ``"genre/vibe"`` to raw CLaMP3 stdout.
    """
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
                print(f"Brak plikow dla {genre}/{vibe} w {actual_gen_dir}, pomijam.")
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
    return results


# ---------------------------------------------------------------------------
# Aggregated by genre (all vibes pooled)
# ---------------------------------------------------------------------------


def evaluate_clamp3_by_genre(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_by_genre.txt",
    midi_subpath: Optional[str] = None,
) -> dict:
    """Compare generated vs reference MIDI aggregated per genre across all vibes.

    All MIDI files from every vibe of a given genre are merged into a single
    temporary directory before scoring, giving a genre-level similarity measure.

    Args:
        generated_dir: Root of generated MIDI files (``genre/vibe/[midi_subpath]/``).
        reference_dir: Root of reference MIDI files (``genre/vibe/``).
        results_dir: Directory where the results text file is written.
        results_filename: Name of the output file.
        midi_subpath: Optional sub-path inside each generated vibe directory.

    Returns:
        Dict mapping genre name to raw CLaMP3 stdout.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / results_filename
    env = _make_env()
    results = {}

    genres = sorted(
        d.name for d in reference_dir.iterdir() if d.is_dir() and not d.name.startswith("_")
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
            print(f"Brak plikow MIDI dla gatunku {genre}, pomijam.")
            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)
            continue

        results[genre] = _run_clamp3(tmp_gen, tmp_ref, f"{genre} (wszystkie viby)", env)

        shutil.rmtree(tmp_gen)
        shutil.rmtree(tmp_ref)

    _save_results(results, results_file, section_suffix="[wszystkie viby]")
    return results


# ---------------------------------------------------------------------------
# Aggregated by vibe (all genres pooled)
# ---------------------------------------------------------------------------


def evaluate_clamp3_by_vibe(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    results_filename: str = "clamp3_by_vibe.txt",
    midi_subpath: Optional[str] = None,
) -> dict:
    """Compare generated vs reference MIDI aggregated per vibe across all genres.

    All MIDI files from every genre of a given vibe are merged into a single
    temporary directory before scoring, giving a vibe-level similarity measure.

    Args:
        generated_dir: Root of generated MIDI files (``genre/vibe/[midi_subpath]/``).
        reference_dir: Root of reference MIDI files (``genre/vibe/``).
        results_dir: Directory where the results text file is written.
        results_filename: Name of the output file.
        midi_subpath: Optional sub-path inside each generated vibe directory.

    Returns:
        Dict mapping vibe name to raw CLaMP3 stdout.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / results_filename
    env = _make_env()
    results = {}

    vibes = sorted(
        {
            vibe_dir.name
            for genre_dir in reference_dir.iterdir()
            if genre_dir.is_dir() and not genre_dir.name.startswith("_")
            for vibe_dir in genre_dir.iterdir()
            if vibe_dir.is_dir() and not vibe_dir.name.startswith("_")
        }
    )

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
            print(f"Brak plikow MIDI dla vibu {vibe}, pomijam.")
            shutil.rmtree(tmp_gen)
            shutil.rmtree(tmp_ref)
            continue

        results[vibe] = _run_clamp3(tmp_gen, tmp_ref, f"{vibe} (wszystkie gatunki)", env)

        shutil.rmtree(tmp_gen)
        shutil.rmtree(tmp_ref)

    _save_results(results, results_file, section_suffix="[wszystkie gatunki]")
    return results


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------


def evaluate_all_clamp3(
    generated_dir: Path,
    reference_dir: Path,
    results_dir: Path,
    model_name: str = "model",
    midi_subpath: Optional[str] = None,
) -> dict:
    """Run all three CLaMP3 comparison modes and return combined results.

    Executes in order:
    1. Per (genre, vibe) pair.
    2. Per genre (all vibes aggregated).
    3. Per vibe (all genres aggregated).

    Args:
        generated_dir: Root of generated MIDI files.
        reference_dir: Root of reference MIDI files.
        results_dir: Directory where result files are written.
        model_name: Prefix used in output filenames (e.g. ``"midillm"``).
        midi_subpath: Optional sub-path inside each generated vibe directory.

    Returns:
        Dict with keys ``"genre_vibe"``, ``"by_genre"``, ``"by_vibe"``, each
        mapping to the results dict returned by the corresponding function.
    """
    sep = "=" * 60

    print(f"\n{sep}\nCLaMP3: genre/vibe -- {model_name}\n{sep}")
    gv = evaluate_with_clamp3(
        generated_dir,
        reference_dir,
        results_dir,
        results_filename=f"{model_name}_genre_vibe_clamp3.txt",
        midi_subpath=midi_subpath,
    )

    print(f"\n{sep}\nCLaMP3: per gatunek -- {model_name}\n{sep}")
    bg = evaluate_clamp3_by_genre(
        generated_dir,
        reference_dir,
        results_dir,
        results_filename=f"{model_name}_by_genre_clamp3.txt",
        midi_subpath=midi_subpath,
    )

    print(f"\n{sep}\nCLaMP3: per vibe -- {model_name}\n{sep}")
    bv = evaluate_clamp3_by_vibe(
        generated_dir,
        reference_dir,
        results_dir,
        results_filename=f"{model_name}_by_vibe_clamp3.txt",
        midi_subpath=midi_subpath,
    )

    return {"genre_vibe": gv, "by_genre": bg, "by_vibe": bv}
