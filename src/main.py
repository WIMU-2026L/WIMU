"""Entry point for the WIMU music generation and evaluation pipeline.

Usage examples::

    python src/main.py organize

    python src/main.py generate --n_outputs 3
    python src/main.py evaluate --model all
    python src/main.py evaluate --model midillm --mode by_genre
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import argparse
import logging

from config import (
    MIDILLM_OUTPUT_DIR,
    MUSECOCO_MIDI_SUBPATH,
    MUSECOCO_OUTPUT_DIR,
    RESULTS_DIR,
    WANDB_ENTITY,
    WANDB_PROJECT,
    XMIDI_ORGANIZED_DIR,
)
from data.dataset_processing import organize_midi_files
from metrics.clamp3 import (
    evaluate_all_clamp3,
    evaluate_clamp3_by_genre,
    evaluate_clamp3_by_vibe,
    evaluate_with_clamp3,
)

from metrics.fmd import (
    evaulate_fmd_all,
    evaulate_fmd_by_vibe,
    evaulate_fmd_by_genre_vibe,
    evaulate_fmd_by_genre,
)

from metrics.wandb_logger import log_clamp3_results
from model.midillm.pipeline import generate_midillm_samples, generate_musecoco_samples

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def cmd_organize(args: argparse.Namespace) -> None:
    """Reorganize the raw XMIDI dataset into genre/vibe folder structure."""
    from config import XMIDI_DATA_DIR

    organize_midi_files(XMIDI_DATA_DIR, XMIDI_ORGANIZED_DIR)


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate MIDI samples using the selected model."""
    if args.model == "midillm":
        generate_midillm_samples(n_outputs=args.n_outputs)
    elif args.model == "musecoco":
        generate_musecoco_samples(n_outputs=args.n_outputs)

    else:
        logger.error("Nieznany model: %s", args.model)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Run CLaMP3 evaluation for the selected model(s) and mode(s)."""
    targets = {
        "midillm": (MIDILLM_OUTPUT_DIR, None),
        "musecoco": (MUSECOCO_OUTPUT_DIR, MUSECOCO_MIDI_SUBPATH),
    }
    models = list(targets.keys()) if args.model == "all" else [args.model]

    for model_name in models:
        gen_dir, midi_subpath = targets[model_name]
        if not gen_dir.exists():
            logger.warning("Brak katalogu generated dla %s: %s", model_name, gen_dir)
            continue
        
        if args.metric == "clamp3":
            if args.mode == "all":
                results = evaluate_all_clamp3(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    model_name=model_name,
                    midi_subpath=midi_subpath,
                )
                log_clamp3_results(
                    results,
                    run_name=f"clamp3-{model_name}",
                    project=WANDB_PROJECT,
                    entity=WANDB_ENTITY,
                    extra_config={"model": model_name, "mode": "all"},
                )
            elif args.mode == "genre_vibe":
                evaluate_with_clamp3(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_genre_vibe_clamp3.txt",
                    midi_subpath=midi_subpath,
                )
            elif args.mode == "by_genre":
                evaluate_clamp3_by_genre(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_by_genre_clamp3.txt",
                    midi_subpath=midi_subpath,
                )
            elif args.mode == "by_vibe":
                evaluate_clamp3_by_vibe(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_by_vibe_clamp3.txt",
                    midi_subpath=midi_subpath,
                )
        elif args.metric == "fmd":
            if args.mode == "all":
                results = evaulate_fmd_all(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    model_name=model_name,
                    midi_subpath=midi_subpath,
                )

            elif args.mode == "genre_vibe":
                evaulate_fmd_by_genre_vibe(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_genre_vibe_fmd.json",
                    midi_subpath=midi_subpath,
                )
            elif args.mode == "by_genre":
                evaulate_fmd_by_genre(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_by_genre_fmd.json",
                    midi_subpath=midi_subpath,
                )
            elif args.mode == "by_vibe":
                evaulate_fmd_by_vibe(
                    generated_dir=gen_dir,
                    reference_dir=XMIDI_ORGANIZED_DIR,
                    results_dir=RESULTS_DIR,
                    results_filename=f"{model_name}_by_vibe_fmd.json",
                    midi_subpath=midi_subpath,
                )

        


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="wimu",
        description="WIMU - Music Generation Quality Evaluation Pipeline",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- organize ---
    subparsers.add_parser(
        "organize",
        help="Reorganize raw XMIDI dataset into genre/vibe folder structure",
    )

    # --- generate ---
    gen = subparsers.add_parser("generate", help="Generate MIDI samples with a model")
    gen.add_argument(
        "--model",
        choices=["midillm", "musecoco"],
        default="midillm",
        help="Model to use for generation (default: midillm)",
    )
    gen.add_argument(
        "--n_outputs",
        type=int,
        default=1,
        metavar="N",
        help="Number of MIDI files to generate per prompt (default: 1)",
    )

    # --- evaluate ---
    ev = subparsers.add_parser("evaluate", help="Evaluate generated MIDI with CLaMP3")
    ev.add_argument(
        "--model",
        choices=["midillm", "musecoco", "all"],
        default="all",
        help="Model to evaluate (default: all)",
    )
    ev.add_argument(
        "--mode",
        choices=["all", "genre_vibe", "by_genre", "by_vibe"],
        default="all",
        help="Comparison granularity (default: all)",
    )
    ev.add_argument(
        "--metric",
        choices=[ "fmd", "clamp3"],
        default="all",
        help="Choose metric to evaluate models (default: all)",
    )


    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "organize": cmd_organize,
        "generate": cmd_generate,
        "evaluate": cmd_evaluate,
    }
    dispatch[args.command](args)
