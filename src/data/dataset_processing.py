import shutil

def organize_midi_files(XMIDI_DIR, OUTPUT_DIR):
    if not XMIDI_DIR.is_dir():
        raise FileNotFoundError(f"XMIDI source directory does not exist: {XMIDI_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copied_files = 0

    for midi_file in XMIDI_DIR.glob("*.midi"):
        parts = midi_file.stem.split("_")
        # XMIDI_{vibe}_{genre}_{id} → parts = ['XMIDI', vibe, genre, id]
        
        if len(parts) < 4 or parts[0] != "XMIDI":
            print(f"Pomijam (nieznany format): {midi_file.name}")
            continue

        vibe = parts[1]
        genre = parts[2]

        target_dir = OUTPUT_DIR / genre / vibe
        target_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy(midi_file, target_dir / midi_file.name)
        copied_files += 1

    print(f"Gotowe! Skopiowano {copied_files} plikow MIDI.")
