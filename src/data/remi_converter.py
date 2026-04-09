from pathlib import Path

from miditok import REMI, TokSequence, TokenizerConfig


POSITION_RESOLUTION = 12
DEFAULT_TIME_SIGNATURE = "4/4"


def create_tokenizer() -> REMI:
    config = TokenizerConfig(
        use_programs=True,
        use_time_signatures=True,
        one_token_stream_for_programs=True,
        beat_res={(0, 4): POSITION_RESOLUTION},
    )
    return REMI(config)


TOKENIZER = create_tokenizer()


def load_remi_tokens(file_path: Path) -> list[str]:
    return file_path.read_text().split()


def split_command_tokens(tokens: list[str]) -> tuple[list[str], list[str]]:
    if "<sep>" not in tokens:
        return [], tokens

    separator_index = tokens.index("<sep>")
    return tokens[:separator_index], tokens[separator_index + 1:]


def make_bar_tokens(value: int) -> list[str]:
    return ["Bar_None"] * value


def make_position_token(value: int) -> str:
    return f"Position_{value}"


def make_program_token(value: int) -> str:
    if value == 128:
        return "Program_-1"

    return f"Program_{value}"


def make_pitch_token(program_token: str, value: int) -> str:
    if program_token == "Program_-1":
        return f"PitchDrum_{value - 128}"

    return f"Pitch_{value}"


def make_duration_token(value: int) -> str:
    beats, positions = divmod(value, POSITION_RESOLUTION)
    return f"Duration_{beats}.{positions}.{POSITION_RESOLUTION}"


def make_velocity_token(value: int) -> str:
    velocity = max(3, min(127, value * 4 - 1))
    velocity -= (velocity - 3) % 4
    return f"Velocity_{velocity}"


def make_note_tokens(program_token: str, pitch: int, duration: int, velocity: int) -> list[str]:
    return [
        make_pitch_token(program_token, pitch),
        make_velocity_token(velocity),
        make_duration_token(duration),
    ]


def convert_remi_tokens_to_miditok_tokens(tokens: list[str]) -> list[str]:
    converted_tokens = [f"TimeSig_{DEFAULT_TIME_SIGNATURE}", "Bar_None"]
    current_program_token = "Program_0"
    current_pitch = None
    current_duration = None

    for token in tokens:
        prefix, _, raw_value = token.partition("-")
        if not raw_value:
            continue

        value = int(raw_value)

        if prefix == "b":
            converted_tokens.extend(make_bar_tokens(value))
            continue

        if prefix == "o":
            converted_tokens.append(make_position_token(value))
            continue

        if prefix == "i":
            current_program_token = make_program_token(value)
            converted_tokens.append(current_program_token)
            continue

        if prefix == "p":
            current_pitch = value
            continue

        if prefix == "d":
            current_duration = value
            continue

        if prefix == "v":
            if current_pitch is None or current_duration is None:
                continue

            converted_tokens.extend(
                make_note_tokens(
                    current_program_token,
                    current_pitch,
                    current_duration,
                    value,
                )
            )
            current_pitch = None
            current_duration = None

    return converted_tokens


def convert_remi_file_to_midi(source_path: Path, target_path: Path) -> Path:
    tokens = load_remi_tokens(source_path)
    _, remi_tokens = split_command_tokens(tokens)
    miditok_tokens = convert_remi_tokens_to_miditok_tokens(remi_tokens)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    score = TOKENIZER.decode(TokSequence(tokens=miditok_tokens))
    score.dump_midi(target_path)
    return target_path
