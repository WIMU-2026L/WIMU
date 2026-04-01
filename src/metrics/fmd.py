from frechet_music_distance import FrechetMusicDistance

def calculate_fmd(reference_path: str, test_path: str) -> float:
    metric = FrechetMusicDistance(verbose=True)
    score = metric.score(
        reference_path=reference_path,
        test_path=test_path
    )
    return score


def calculate_fmd_inf(reference_path: str, test_path: str, steps=25, min_n=5):
    metric = FrechetMusicDistance(verbose=True)
    score = metric.score_inf(
        reference_path=reference_path,
        test_path=test_path,
        steps=steps,
        min_n=min_n
    )
    return score