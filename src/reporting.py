from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def count_midi_files(data_dir: Path) -> int:
    return len(list(data_dir.rglob("*.midi")))


def make_fmd_inf_data(result) -> dict:
    return {
        "score": result.score,
        "r2": result.r2,
        "slope": result.slope,
        "points": result.points,
    }


def make_comparison(
    reference_genre: str,
    test_genre: str,
    reference_path: Path,
    test_path: Path,
    fmd_score: float,
    fmd_inf_result,
) -> dict:
    return {
        "reference_genre": reference_genre,
        "test_genre": test_genre,
        "reference_path": str(reference_path),
        "test_path": str(test_path),
        "reference_count": count_midi_files(reference_path),
        "test_count": count_midi_files(test_path),
        "fmd_score": fmd_score,
        "fmd_inf": make_fmd_inf_data(fmd_inf_result),
    }


def make_summary(comparisons: list[dict]) -> dict:
    best_pair = min(comparisons, key=lambda comparison: comparison["fmd_inf"]["score"])
    worst_pair = max(comparisons, key=lambda comparison: comparison["fmd_inf"]["score"])

    return {
        "total_reference_genres": len({comparison["reference_genre"] for comparison in comparisons}),
        "total_generated_genres": len({comparison["test_genre"] for comparison in comparisons}),
        "total_comparisons": len(comparisons),
        "best_pair": best_pair,
        "worst_pair": worst_pair,
    }


def render_report(template_dir: Path, template_name: str, context: dict) -> str:
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template(template_name)
    return template.render(**context)


def write_report(
    template_dir: Path,
    template_name: str,
    output_path: Path,
    title: str,
    experiment_name: str,
    reference_root: Path,
    test_root: Path,
    comparisons: list[dict],
    fmd_inf_steps: int,
    fmd_inf_min_n: int,
) -> Path:
    context = {
        "title": title,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "experiment_name": experiment_name,
        "reference_root": str(reference_root),
        "test_root": str(test_root),
        "fmd_inf_steps": fmd_inf_steps,
        "fmd_inf_min_n": fmd_inf_min_n,
        "comparisons": comparisons,
        "summary": make_summary(comparisons),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(template_dir, template_name, context))
    return output_path
