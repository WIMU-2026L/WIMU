"""Utilities for reorganizing the raw XMIDI dataset into a structured layout."""

import shutil
from pathlib import Path


def organize_midi_files(xmidi_dir: Path, output_dir: Path) -> None:
    """Copy XMIDI ``.midi`` files into a ``genre/vibe/`` folder hierarchy.

    The XMIDI dataset names files as ``XMIDI_{vibe}_{genre}_{id}.midi``.
    This function reads that naming convention and creates the directory
    structure ``output_dir/{genre}/{vibe}/`` without modifying the originals.

    Args:
        xmidi_dir: Directory containing the raw flat XMIDI ``.midi`` files.
        output_dir: Root of the target folder hierarchy.
    """
    for midi_file in xmidi_dir.glob("*.midi"):
        parts = midi_file.stem.split("_")
        # Expected format: XMIDI_{vibe}_{genre}_{id}
        if len(parts) < 4 or parts[0] != "XMIDI":
            print(f"Pomijam (nieznany format): {midi_file.name}")
            continue

        vibe = parts[1]
        genre = parts[2]

        target_dir = output_dir / genre / vibe
        target_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(midi_file, target_dir / midi_file.name)

    print("Gotowe!")
