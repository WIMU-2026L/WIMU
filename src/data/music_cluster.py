import os
from tqdm import tqdm
import json
from pathlib import Path
import tempfile
import argparse
from frechet_music_distance import FrechetMusicDistance
import mido


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
        # if self.duration_analysis:
        #     duration = get_midi_length(file_path)

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
    
def group_xmidi_files(target_dir, duration_analysis=0):
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

def group_musecoco_files(target_dir, duration_analysis=0):
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
