from frechet_music_distance import FrechetMusicDistance
import os
from tqdm import tqdm
import json
from pathlib import Path
import tempfile
from midiprocessor.midi_decoding import MidiDecoder
import argparse
from frechet_music_distance import FrechetMusicDistance
import mido
from data.music_cluster import *


VERBOSE = True

def calculate_fmd(reference_path: str, test_path: str) -> float:
    metric = FrechetMusicDistance(verbose=VERBOSE)
    score = metric.score(reference_path=reference_path, test_path=test_path)
    return score


def calculate_fmd_individual(reference_path: str, test_path: str) -> float:
    if len(test_path) != 0:
        print("[Warning] Using individual function for more than one test path.")
    test_path = test_path[0]
    metric = FrechetMusicDistance(verbose=VERBOSE)
    score = metric.score_individual(reference_path=reference_path, test_path=test_path)
    return score


def calculate_fmd_inf(reference_path: str, test_path: str, steps=25, min_n=5):
    metric = FrechetMusicDistance(verbose=VERBOSE)
    score = metric.score_inf(
        reference_path=reference_path, test_path=test_path, steps=steps, min_n=min_n
    )
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
    
def evaulate_fmd_by_genre(generated_dir, reference_dir, results_dir, model_name, midi_subpath):
    print("Runing evaluation for fmd genre")
    ref_cluster = group_musecoco_files(reference_dir)
    test_cluster = group_musecoco_files(generated_dir)
    return
    score = calculate_fmd_genres(ref_cluster, test_cluster)
    with open(results_dir + f"/{model_name}_fmd_scores_by_genre.json", 'w') as fp:
        json.dump(score, fp)

def evaulate_fmd_by_vibe(generated_dir, reference_dir, results_dir, model_name, midi_subpath):
    print("Runing evaluation for fmd vibe")
    ref_cluster = group_musecoco_files(reference_dir)
    test_cluster = group_musecoco_files(generated_dir)
    return
    score = calculate_fmd_moods(ref_cluster, test_cluster)
    with open(results_dir + f"/{model_name}_fmd_scores_by_mood.json", 'w') as fp:
        json.dump(score, fp)


def evaulate_fmd_by_genre_vibe(generated_dir, reference_dir, results_dir, model_name, midi_subpath):
    print("Runing evaluation for fmd genre vibe")
    ref_cluster = group_musecoco_files(reference_dir)
    test_cluster = group_musecoco_files(generated_dir)
    return
    score = calculate_fmd_genres_moods(ref_cluster, test_cluster)
    with open(results_dir + f"/{model_name}_fmd_scores_by_genre_vibe.json", 'w') as fp:
        json.dump(score, fp)



def evaulate_fmd_all(generated_dir, reference_dir, results_dir, model_name, midi_subpath):
    print("Runing evaluation for fmd all")
    evaulate_fmd_by_genre_vibe(generated_dir, reference_dir, results_dir, model_name, midi_subpath)
    evaulate_fmd_by_genre(generated_dir, reference_dir, results_dir, model_name, midi_subpath)
    evaulate_fmd_by_vibe(generated_dir, reference_dir, results_dir, model_name, midi_subpath)
