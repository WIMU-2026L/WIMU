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

if __name__ == "__main__":
    ref_path = "/home/arion/Workspace-private/WIMU/WIMU/muzic/musecoco/2-attribute2music_model/generation/0505/linear_mask-1billion-attribute2music_clean/infer/country/angry/topk15-t0.7-ngram16"
    test_path = "/home/arion/Workspace-private/WIMU/WIMU/muzic/musecoco/2-attribute2music_model/generation/0505/linear_mask-1billion-attribute2music_clean/infer/jazz/angry/topk15-t0.7-ngram16"
    print(calculate_fmd(ref_path, test_path))