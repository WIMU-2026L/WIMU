import json
from enum import Enum
from pathlib import Path


class Genres(Enum):
    NEW_AGE = "new age"
    ELECTRONIC = "electronic"
    RAP = "rap"
    RELIGIOUS = "religious"
    INTERNATIONAL = "international"
    EASY_LISTENING = "easy listening"
    AVANT_GARDE = "avant garde"
    RNB = "rnb"
    LATIN = "latin"
    CHILDREN = "children"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    COMEDY = "comedy"
    POP = "pop"
    REGGAE = "reggae"
    STAGE = "stage"
    FOLK = "folk"
    BLUES = "blues"
    VOCAL = "vocal"
    HOLIDAY = "holiday"
    COUNTRY = "country"
    SYMPHONY = "symphony"


def load_infer_command(file_path: Path) -> dict:
    return json.loads(file_path.read_text())


def load_infer_command_tokens(file_path: Path) -> list[str]:
    infer_command = load_infer_command(file_path)
    return infer_command.get("infer_command_tokens", [])


def make_genre_token(index: int) -> str:
    return f"S4_{index}_0"


def extract_genres_from_tokens(tokens: list[str]) -> list[str]:
    genres = []

    for index, genre in enumerate(Genres):
        if make_genre_token(index) in tokens:
            genres.append(genre.value)

    return genres


def extract_genres(file_path: Path) -> list[str]:
    return extract_genres_from_tokens(load_infer_command_tokens(file_path))


def slugify_genre(genre: str) -> str:
    return genre.replace(" ", "_")


def make_file_stem(genres: list[str], original_folder: str, original_file_name: str) -> str:
    if not genres:
        genre_part = "unknown"
    else:
        slugified_genres = [slugify_genre(genre) for genre in genres]
        genre_part = "_".join(slugified_genres)

    return f"musecoco_generated_{genre_part}_{original_folder}_{original_file_name}"


def make_unique_file_path(target_dir: Path, stem: str) -> Path:
    target_path = target_dir / f"{stem}.midi"
    suffix = 1

    while target_path.exists():
        target_path = target_dir / f"{stem}_{suffix}.midi"
        suffix += 1

    return target_path


def make_generated_midi_path(infer_command_path: Path, remi_file_path: Path, target_dir: Path) -> Path:
    genres = extract_genres(infer_command_path)
    original_folder = remi_file_path.parent.parent.name
    original_file_name = remi_file_path.stem
    stem = make_file_stem(genres, original_folder, original_file_name)
    return make_unique_file_path(target_dir, stem)
