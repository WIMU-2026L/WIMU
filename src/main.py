import argparse
from pathlib import Path
from typing import Optional, Tuple

from config import (
    MIDILLM_GENERATED_DIR,
    MUSECOCO_GENERATED_DIR,
    RESULTS_DIR,
    XMIDI_DATA_DIR,
    XMIDI_ORGANIZED_DIR,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Project CLI for dataset preparation, generation, and evaluation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser(
        "download-data",
        help="Download and extract the XMIDI dataset.",
    )
    download_parser.add_argument(
        "--list-after",
        action="store_true",
        help="Print the number of loaded MIDI samples after download.",
    )

    organize_parser = subparsers.add_parser(
        "organize-xmidi",
        help="Copy XMIDI files into genre/vibe directories.",
    )
    organize_parser.add_argument(
        "--source",
        type=Path,
        default=XMIDI_DATA_DIR,
        help=f"Source directory with flat XMIDI files. Default: {XMIDI_DATA_DIR}",
    )
    organize_parser.add_argument(
        "--output",
        type=Path,
        default=XMIDI_ORGANIZED_DIR,
        help=f"Output directory for organized files. Default: {XMIDI_ORGANIZED_DIR}",
    )

    generate_parser = subparsers.add_parser(
        "generate-midillm",
        help="Generate samples with MIDI-LLM using prepared prompts.",
    )
    generate_parser.add_argument(
        "--n-outputs",
        type=int,
        default=3,
        help="Number of generated outputs per prompt. Default: 3",
    )

    clamp_parser = subparsers.add_parser(
        "eval-clamp3",
        help="Run CLaMP3 evaluation for one of the supported models.",
    )
    clamp_parser.add_argument(
        "--model",
        choices=["midillm", "musecoco"],
        required=True,
        help="Model name used to infer generated data layout.",
    )
    clamp_parser.add_argument(
        "--generated-dir",
        type=Path,
        help="Override the generated samples directory.",
    )
    clamp_parser.add_argument(
        "--reference-dir",
        type=Path,
        default=XMIDI_ORGANIZED_DIR,
        help=f"Reference directory in genre/vibe structure. Default: {XMIDI_ORGANIZED_DIR}",
    )
    clamp_parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help=f"Where result files should be written. Default: {RESULTS_DIR}",
    )

    return parser.parse_args()


def _resolve_generated_dir(
    model: str,
    generated_dir: Optional[Path],
) -> Tuple[Path, Optional[str]]:
    if generated_dir is not None:
        return generated_dir, None
    if model == "musecoco":
        return MUSECOCO_GENERATED_DIR, "topk15-t0.7-ngram16/0/midi"
    return MIDILLM_GENERATED_DIR, None


def main() -> None:
    args = _parse_args()

    if args.command == "download-data":
        from data.data_loader import download_and_extract, load_data

        download_and_extract()
        if args.list_after:
            midi_samples = load_data(XMIDI_DATA_DIR)
            print(f"Loaded {len(midi_samples)} MIDI samples.")
        return

    if args.command == "organize-xmidi":
        from data.dataset_processing import organize_midi_files

        organize_midi_files(args.source, args.output)
        print(f"Organized XMIDI files in {args.output}")
        return

    if args.command == "generate-midillm":
        from model.midillm.pipeline import generate_samples

        generate_samples(n_outputs=args.n_outputs)
        print(f"Generated MIDI-LLM samples in {MIDILLM_GENERATED_DIR}")
        return

    if args.command == "eval-clamp3":
        from metrics.clamp3 import evaluate_all_clamp3

        generated_dir, midi_subpath = _resolve_generated_dir(
            args.model,
            args.generated_dir,
        )
        evaluate_all_clamp3(
            generated_dir=generated_dir,
            reference_dir=args.reference_dir,
            results_dir=args.results_dir,
            model_name=args.model,
            midi_subpath=midi_subpath,
        )
        print(f"Saved CLaMP3 results for {args.model} in {args.results_dir}")
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
