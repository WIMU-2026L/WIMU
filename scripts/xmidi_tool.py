import os
from tqdm import tqdm
import json
from pathlib import Path
import tempfile
import argparse

midi_decoder = None

VERBOSE = True


def _get_midi_decoder():
    global midi_decoder
    if midi_decoder is None:
        from midiprocessor.midi_decoding import MidiDecoder

        midi_decoder = MidiDecoder("REMIGEN2")
    return midi_decoder


def _create_fmd_metric():
    from frechet_music_distance import FrechetMusicDistance

    return FrechetMusicDistance(verbose=VERBOSE)


def calculate_fmd(reference_path: str, test_path: str) -> float:
    metric = _create_fmd_metric()
    score = metric.score(reference_path=reference_path, test_path=test_path)
    return score


def calculate_fmd_individual(reference_path: str, test_path: str) -> float:
    if len(test_path) != 0:
        print("[Warning] Using individual function for more than one test path.")
    test_path = test_path[0]
    metric = _create_fmd_metric()
    score = metric.score_individual(reference_path=reference_path, test_path=test_path)
    return score


def calculate_fmd_inf(reference_path: str, test_path: str, steps=25, min_n=5):
    metric = _create_fmd_metric()
    score = metric.score_inf(
        reference_path=reference_path, test_path=test_path, steps=steps, min_n=min_n
    )
    return score


class MusicCluster:
    def __init__(self):
        self.genres_dict = {}
        self.duration_analysis = False
        self.stats = {
            "total_files": 0,
            "total_duration": 0,
            "shortest": float("inf"),
            "longest": 0,
            "shortest_name": "",
            "longest_name": "",
            "skipped_files": 0,
        }

    def set_duration_analysis(self, bool_value):
        self.duration_analysis = bool_value

    def add(self, file_path, genre, mood):

        duration = 0
        if self.duration_analysis:
            duration = get_midi_length(file_path)

        if genre not in self.genres_dict:
            self.genres_dict[genre] = {}

        if mood not in self.genres_dict[genre]:
            self.genres_dict[genre][mood] = []

        # store precaluclated staticits in file info object
        self.genres_dict[genre][mood].append({"name": file_path, "duration": duration})

        # Aktualizacja ogólnych statystyk (tylko dla poprawnych plików MIDI)
        if not self.duration_analysis or duration > 0:
            self.stats["total_files"] += 1
            self.stats["total_duration"] += duration

            if duration > self.stats["longest"]:
                self.stats["longest"] = duration
                self.stats["longest_name"] = file_path

            if duration < self.stats["shortest"]:
                self.stats["shortest"] = duration
                self.stats["shortest_name"] = file_path

    def get_grouped_by_moods(self):
        moods = {}
        for genre, moods_dict in self.genres_dict.items():
            for mood, file_datas in moods_dict.items():
                paths = moods.get(mood, [])
                for data in file_datas:
                    paths.append(data["name"])
                moods[mood] = paths
        return moods

    def get_grouped_by_genres(self):
        genres = {}
        for genre, moods_dict in self.genres_dict.items():
            for mood, file_datas in moods_dict.items():
                paths = genres.get(genre, [])
                for data in file_datas:
                    paths.append(data["name"])
                genres[genre] = paths
        return genres

    def __str__(self):
        output = ""
        output += "\n" + "=" * 60 + "\n"
        output += " MIDI FILES SUMMARY\n"
        output += "=" * 60 + "\n"

        if self.stats["total_files"] == 0:
            output += "No MIDI files with a valid format were found,\n\n"
            output += "or there was a problem reading them.\n"
            return

        # general stats
        output += "📌 GENERAL STATISTICS:\n"
        output += f" • Valid MIDI files    : {self.stats['total_files']}\n"
        output += (
            f" • Skipped files       : {self.stats['skipped_files']} (invalid name)\n"
        )

        if self.duration_analysis:
            avg_total_dur = self.stats["total_duration"] / self.stats["total_files"]
            output += f" • Avg track duration  : {avg_total_dur:.2f} sec\n"

            if self.stats["longest_name"]:
                output += f" • Longest file        : {self.stats['longest_name']} ({self.stats['longest']:.2f} sec)\n"
                output += f" • Shortest file       : {self.stats['shortest_name']} ({self.stats['shortest']:.2f} sec)\n"

        output += "\n STRUCTURE (GENRES and MOODS):\n"
        output += "-" * 60 + "\n"

        # Detailed statistics from dictionary
        output += "CALCULATING STATS\n\n"
        j = 0
        for genre, moods in self.genres_dict.items():
            j += 1
            # Calculate total files for a given genre
            genre_count = sum(len(files) for files in moods.values())
            output += f"{j:2} Genre: {genre.upper()} (Total files: {genre_count})\n"
            i = 0
            for mood, files in moods.items():
                i += 1
                mood_count = len(files)
                mood_total_dur = sum(f["duration"] for f in files)
                avg_mood_dur = mood_total_dur / mood_count if mood_count > 0 else 0

                output += f"  {i:2}└── Mood: {mood:<10} | Files: {mood_count:<3} | Avg duration: {avg_mood_dur:.2f} sec\n"

        output += "=" * 60 + "\n\n"
        return output


def get_midi_length(file_path):
    """Reading length of track in sec."""
    try:
        import mido

        mid = mido.MidiFile(file_path)
        return mid.length
    except Exception:
        # Zwraca 0 w przypadku problemu z odczytem pliku
        return 0


def group_xmidi_files(target_dir, duration_analysis):
    if not os.path.isdir(target_dir):
        print(f"[Error] Path '{target_dir}' is not directory.")
        return
    music_cluster = MusicCluster()
    music_cluster.set_duration_analysis(duration_analysis)

    # Lista wszystkich plików w folderze
    files = [
        f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))
    ]

    print("GROUPPING FILES\n")

    for file_name in tqdm(files):
        # Rozdzielamy nazwę na części.
        # Zamiast rsplit używamy split, by sprawdzić wszystkie 4 segmenty
        # XMIDI_warm_pop_V1UFY7EF.midi -> ['XMIDI', 'warm', 'pop', 'V1UFY7EF.midi']
        parts = file_name.split("_")

        if len(parts) != 4 or parts[0] != "XMIDI":
            music_cluster.stats["skipped_files"] += 1
            continue

        mood = parts[1]
        genre = parts[2]

        file_path = os.path.join(target_dir, file_name)

        music_cluster.add(file_path, genre, mood)

    return music_cluster


def retrive_recursive_all_midi(path):
    midi_filepaths = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            if file_path.endswith((".mid", ".midi")):
                midi_filepaths.append(file_path)
        elif os.path.isdir(file_path):
            inner_midis = retrive_recursive_all_midi(file_path)
            midi_filepaths += inner_midis
    return midi_filepaths


def group_musecoco_files(target_dir, duration_analysis):
    if not os.path.isdir(target_dir):
        print(f"[Error] Path '{target_dir}' is not directory.")
        return
    music_cluster = MusicCluster()
    music_cluster.set_duration_analysis(duration_analysis)

    genres = []
    for genre in os.listdir(target_dir):
        genre_path = os.path.join(target_dir, genre)
        if os.path.isdir(genre_path):
            genres.append((genre, genre_path))
            for mood in os.listdir(genre_path):
                mood_path = os.path.join(genre_path, mood)
                if os.path.isdir(mood_path):
                    midi_files = retrive_recursive_all_midi(mood_path)
                    for file in midi_files:
                        music_cluster.add(file, genre, mood)
                else:
                    raise Exception(
                        f"Unexpected file which is not dir, investigate: {mood_path}"
                    )

        else:
            raise Exception(
                f"Unexpected file which is not dir, investigate: {genre_path}"
            )

    return music_cluster


def generate_prompts(prompt_example_path, out_dir, music_cluster):
    if music_cluster is None:
        raise ValueError("Prompt generation requires a valid, existing cluster directory.")

    genres_dict = music_cluster.genres_dict

    with open(prompt_example_path, "r") as fp:
        prompt_example_text = fp.readline()
    prompt_text = ""
    for genre in genres_dict.keys():
        for mood in genres_dict[genre].keys():
            prompt_text = prompt_example_text.replace("{MOOD}", mood)
            prompt_text = prompt_text.replace("{GENRE}", genre)
            os.makedirs(out_dir, exist_ok=True)
            file_name = f"{genre}_{mood}.txt"

            with open(os.path.join(out_dir, file_name), "w") as fp:
                fp.write(prompt_text)


def load_cluster(target_dir, cluster_type="auto", duration_analysis=False):
    if cluster_type == "xmidi":
        return group_xmidi_files(target_dir, duration_analysis)
    if cluster_type == "musecoco":
        return group_musecoco_files(target_dir, duration_analysis)

    if not os.path.isdir(target_dir):
        print(f"[Error] Path '{target_dir}' is not directory.")
        return None

    has_root_midis = any(
        os.path.isfile(os.path.join(target_dir, file_name))
        and file_name.endswith((".mid", ".midi"))
        for file_name in os.listdir(target_dir)
    )
    if has_root_midis:
        return group_xmidi_files(target_dir, duration_analysis)
    return group_musecoco_files(target_dir, duration_analysis)


def merge_jsons(dir_path, music_cluster):
    genres_dict = music_cluster.genres_dict
    merged_prompts = {}
    for genre in genres_dict.keys():
        merged_prompts[genre] = {}
        dir_path_genre = dir_path + "/" + genre
        for mood in genres_dict[genre].keys():
            file_name = mood + "_" + genre + "_prompts.json"
            with open(dir_path_genre + "/" + file_name, "r") as fp:
                mood_json = json.load(fp)
                merged_prompts[genre][mood] = mood_json
    with open(dir_path + "/all_prompts.json", "w") as fp:
        json.dump(merged_prompts, fp)


def process_all_remi_to_midi(root_directory):
    """
    Searching 'remi' directories for .txt files with remi content,
    converts to '.mid' format.
    """
    root_path = Path(root_directory)

    # Używamy rglob do znalezienia wszystkich plików .txt w jakimkolwiek folderze 'remi'
    remi_files = list(root_path.rglob("remi/*.txt"))

    if not remi_files:
        print("Not found .txt in 'remi' dirs. Check root_directory.")
        return

    print(f"Znaleziono {len(remi_files)} plików do przetworzenia.")

    e_files = []
    e_cnt = 0
    c_cnt = 0
    for txt_file in remi_files:
        print(f"\nProcessing: {txt_file}")

        # Ustalanie ścieżek
        # txt_file.parent to folder 'remi'
        # txt_file.parent.parent to nadrzędny folder z ID (np. '0', '1')
        id_folder = txt_file.parent.parent
        midi_dir = id_folder / "midi"

        # Tworzenie folderu 'midi', jeśli jeszcze nie istnieje
        midi_dir.mkdir(parents=True, exist_ok=True)

        # Docelowa ścieżka pliku MIDI (ta sama nazwa, ale rozszerzenie .mid)
        midi_file_path = midi_dir / f"{txt_file.stem}.mid"

        try:
            generate_midi_from_remi(txt_file, midi_file_path)
            c_cnt += 1
        except Exception as e:
            print(f"  [Error] With the file {txt_file.name}: {e}")
            e_files.append(txt_file)
            e_cnt += 1

    print("Processing finished.")
    print("\nSUMMARY\n")
    print(f"Files found: {len(remi_files)}\n")
    print(f"Correctly processed: {c_cnt}\n")
    print(f"Number of files impossible to process: {e_cnt}\n")
    print("File paths:")
    for p in e_files:
        print("\t", p)


def generate_midi_from_remi(remi_path, midi_path):
    with open(remi_path, "r", encoding="utf-8") as f:
        remi_text = f.read().strip()

    if not remi_text:
        print("\t[Skipped] File is empty.")
        return

    tokens = remi_text.split(" ")

    if "<sep>" in tokens:
        sep_index = tokens.index("<sep>")
        tokens = tokens[sep_index + 1 :]
    else:
        tokens = [t for t in tokens if "-" in t]

    if not tokens:
        print("\t[Skipped] Not valid tokens found after cleaning.")
        return

    midi_obj = _get_midi_decoder().decode_from_token_str_list(tokens)

    midi_obj.dump(str(midi_path))
    print(f"  [Success] Saved to: {midi_path}")


def calculate_fmd_for_custom_group(reference_file_paths, test_file_paths, fmd_function):
    """
    file_paths_list: list of paths to files, np. ['dirA/file1.mid', 'dirB/file2.mid']
    """

    if len(test_file_paths) == 1:
        print(
            f"[Warining] One file is not enough to calculate FMD. USE individual fun. Test files: {test_file_paths}"
        )

    # create tmp dir
    with tempfile.TemporaryDirectory() as ref_dir, tempfile.TemporaryDirectory() as test_dir:
        ref_path = Path(ref_dir)
        test_path = Path(test_dir)

        for i, file_path in enumerate(reference_file_paths):
            oryginal_path = Path(file_path).resolve()

            symlink_name = f"{i}_{oryginal_path.name}"
            symlink_path = ref_path / symlink_name

            os.symlink(oryginal_path, symlink_path)

        for i, file_path in enumerate(test_file_paths):
            oryginal_path = Path(file_path).resolve()

            # add index i to file name, bc files can have same names
            symlink_name = f"{i}_{oryginal_path.name}"
            symlink_path = test_path / symlink_name

            os.symlink(oryginal_path, symlink_path)

        score = fmd_function(ref_path, test_path)

        return score


def calculate_fmd_genres(reference_music_cluster, test_music_cluster):
    ref_genres = reference_music_cluster.get_grouped_by_genres()
    test_genres = test_music_cluster.get_grouped_by_genres()
    ref_keys = ref_genres.keys()
    test_keys = test_genres.keys()
    if ref_keys != test_keys:
        raise Exception(
            f"The genres in both clusters are not consistent \n\t{ref_keys}\n\t{test_keys}"
        )

    results = {}

    for key in ref_keys:
        print("=" * 20, "CALCULATING FOR:", key, "=" * 20)
        partial_results = {}

        comp_key = key
        score = calculate_fmd_for_custom_group(
            ref_genres[comp_key], test_genres[key], calculate_fmd
        )
        partial_results[comp_key] = score
        print("\n")
        print("-" * 60)
        print("Calculated FMD for ", key, comp_key)
        print("Score is:\t", score)
        print("-" * 60)
        print("\n")

        results[key] = partial_results

    return results


def calculate_fmd_moods(reference_music_cluster, test_music_cluster):
    ref_moods = reference_music_cluster.get_grouped_by_moods()
    test_moods = test_music_cluster.get_grouped_by_moods()
    ref_keys = ref_moods.keys()
    test_keys = test_moods.keys()
    if ref_keys != test_keys:
        raise Exception(
            f"The moods in both clusters are not consistent \n\t{ref_keys}\n\t{test_keys}"
        )

    results = {}

    for key in ref_keys:
        print("=" * 20, "CALCULATING FOR:", key, "=" * 20)
        score = calculate_fmd_for_custom_group(
            ref_moods[key], test_moods[key], calculate_fmd
        )
        results[key] = score
        print("\n")
        print("-" * 60)
        print("Calculated FMD for ", key)
        print("Score is:\t", score)
        print("-" * 60)
        print("\n")

    return results


def calculate_fmd_genres_moods(reference_music_cluster, test_music_cluster):
    ref_dict = reference_music_cluster.genres_dict
    test_dict = test_music_cluster.genres_dict
    ref_keys = ref_dict.keys()
    test_keys = test_dict.keys()
    if ref_keys != test_keys:
        raise Exception(
            f"The genres in both clusters are not consistent \n\t{ref_keys}\n\t{test_keys}"
        )

    # check if clusters are consistent, it is preferably to got error before calculating huge datasets, isn't it?
    for genre in ref_keys:
        if ref_dict[genre].keys() != test_dict[genre].keys():
            raise Exception(
                f"The moods in both clusters for {genre} are not consistent \n\t{ref_dict[genre].keys()}\n\t{test_dict[genre].keys()}"
            )

    results = {}

    for genre in ref_keys:
        ref_moods_dict = ref_dict[genre]
        test_moods_dict = test_dict[genre]
        moods = ref_moods_dict.keys()
        for mood in moods:
            ref_paths = [data["name"] for data in ref_moods_dict[mood]]
            test_paths = [data["name"] for data in test_moods_dict[mood]]
            print("=" * 20, "CALCULATING FOR:", genre, mood, "=" * 20)
            print(len(ref_paths))
            print(len(test_paths))
            score = -1
            if len(test_paths) < 2:
                score = calculate_fmd_for_custom_group(
                    ref_paths, test_paths, calculate_fmd
                )
            else:
                score = calculate_fmd_for_custom_group(
                    ref_paths, test_paths, calculate_fmd
                )
            key = genre + "-" + mood
            results[key] = score
            print("\n")
            print("-" * 60)
            print("Calculated FMD for ", genre, mood)
            print("Score is:\t", score)
            print("-" * 60)
            print("\n")
    return results


# ==========================================
# CLI (Command Line Interface)
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Tool for processing MIDI files and calculating FMD metrics"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Select the operation to perform"
    )

    # Command: fmd
    fmd_parser = subparsers.add_parser(
        "fmd", help="Calculate Frechet Music Distance (requires xmidi)"
    )
    fmd_parser.add_argument(
        "--xmidi", required=True, help="Path to the folder with xmidi files"
    )
    fmd_parser.add_argument(
        "--xmidi-type",
        choices=["auto", "xmidi", "musecoco"],
        default="auto",
        help="Structure type of the XMIDI reference directory. Default: auto",
    )
    fmd_parser.add_argument(
        "--musecoco", required=False, help="Path to the musecoco folder"
    )
    fmd_parser.add_argument(
        "--midillm", required=False, help="Path to the midillm folder"
    )

    # Command: prompts
    prompts_parser = subparsers.add_parser("prompts", help="Generate prompt files")
    prompts_parser.add_argument(
        "--template",
        required=True,
        help="Path to the prompt template (e.g., data/prompts/prompt_example.txt)",
    )
    prompts_parser.add_argument(
        "--out", required=True, help="Output directory for prompts (e.g., data/prompts)"
    )
    prompts_parser.add_argument(
        "--cluster-dir",
        required=True,
        help="Path to the MIDI folder to extract genres and moods from",
    )
    prompts_parser.add_argument(
        "--cluster-type",
        choices=["xmidi", "musecoco"],
        required=True,
        help="Type of folder structure in cluster-dir",
    )

    # Command: merge
    merge_parser = subparsers.add_parser("merge", help="Merge generated JSON files")
    merge_parser.add_argument(
        "--dir",
        required=True,
        help="Directory containing JSON prompts (e.g., data/prompts)",
    )
    merge_parser.add_argument(
        "--cluster-dir",
        required=True,
        help="Path to the MIDI folder (required to build the genre/mood tree)",
    )
    merge_parser.add_argument(
        "--cluster-type",
        choices=["xmidi", "musecoco"],
        required=True,
        help="Type of folder structure in cluster-dir",
    )

    # Command: remi2midi
    remi2midi_parser = subparsers.add_parser(
        "remi2midi", help="Convert REMI text files to MIDI"
    )
    remi2midi_parser.add_argument(
        "--dir", required=True, help="Path to the main folder with remi files"
    )

    args = parser.parse_args()

    # commends handling:
    if args.command == "fmd":
        print("Loading cluster XMIDI...")
        xmidi_cluster = load_cluster(args.xmidi, args.xmidi_type, False)
        if xmidi_cluster is None:
            raise ValueError("XMIDI reference directory could not be loaded.")
        if args.musecoco:
            print("Loading cluster MuseCoco...")
            musecoco_cluster = load_cluster(args.musecoco, "musecoco", False)
            if musecoco_cluster is None:
                print("Skipping MuseCoco FMD: generated directory is missing.")
            else:
                print("\n--- Calculating for MuseCoco ---")
                musecoco_scores = {
                    "genre-mood": calculate_fmd_genres_moods(
                        xmidi_cluster, musecoco_cluster
                    ),
                    "mood": calculate_fmd_moods(xmidi_cluster, musecoco_cluster),
                    "genre": calculate_fmd_genres(xmidi_cluster, musecoco_cluster),
                }

                with open("results/musecoco-scores.json", "w") as fp:
                    json.dump(musecoco_scores, fp)

        if args.midillm:
            print("Loading cluster MidiLLM...")
            midillm_cluster = load_cluster(args.midillm, "musecoco", False)
            if midillm_cluster is None:
                print("Skipping MidiLLM FMD: generated directory is missing.")
            else:
                print("\n--- Calculating for MidiLLM ---")
                midillm_scores = {
                    "genre-mood": calculate_fmd_genres_moods(
                        xmidi_cluster, midillm_cluster
                    ),
                    "mood": calculate_fmd_moods(xmidi_cluster, midillm_cluster),
                    "genre": calculate_fmd_genres(xmidi_cluster, midillm_cluster),
                }
                with open("results/midillm-scores.json", "w") as fp:
                    json.dump(midillm_scores, fp)

    elif args.command == "prompts":
        if args.cluster_type == "xmidi":
            cluster = group_xmidi_files(args.cluster_dir, False)
        else:
            cluster = group_musecoco_files(args.cluster_dir, False)

        generate_prompts(args.template, args.out, cluster)
        print(f"Finished prompt generting to dir: {args.out}")

    elif args.command == "merge":
        if args.cluster_type == "xmidi":
            cluster = group_xmidi_files(args.cluster_dir, False)
        else:
            cluster = group_musecoco_files(args.cluster_dir, False)

        merge_jsons(args.dir, cluster)
        print(f"Finished merging to: {args.dir}/all_prompts.json")

    elif args.command == "remi2midi":
        process_all_remi_to_midi(args.dir)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
