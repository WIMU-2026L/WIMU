#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from statistics import mean
from typing import Optional

from jinja2 import Environment, FileSystemLoader


CLAMP3_FILES = {
    "midillm": {
        "by_genre": "midillm_by_genre_clamp3.txt",
        "by_vibe": "midillm_by_vibe_clamp3.txt",
        "genre_vibe": "midillm_genre_vibe_clamp3.txt",
    },
    "musecoco": {
        "by_genre": "musecoco_by_genre_clamp3.txt",
        "by_vibe": "musecoco_by_vibe_clamp3.txt",
        "genre_vibe": "musecoco_genre_vibe_clamp3.txt",
    },
}

FMD_FILES = {
    "midillm": "midillm-scores-v1-1-example.json",
    "musecoco": "musecoco-scores-v1.json",
}

LEGACY_SUMMARY = [
    "MIDI-LLM osiąga wyższe wyniki na poziomie zagregowanym (gatunek, nastrój), co wskazuje",
    "na lepsze odwzorowanie ogólnych cech gatunkowych. Na poziomie szczegółowym",
    "(pojedyncza para gatunek × nastrój) MuseCoco nieznacznie przewyższa MIDI-LLM,",
    "co może wynikać z większej liczby próbek query (2 vs 1) oraz innego sposobu",
    "kondycjonowania generacji muzyką symboliczną.",
    "",
    "Nastroje najtrudniejsze do odwzorowania dla obu modeli to **romantic** i **quiet**,",
    "co sugeruje ich subtelny charakter semantyczny w przestrzeni embeddingów CLaMP3.",
    "Najwyższe wyniki osiągane są konsekwentnie dla nastrojów **funny** i **fear**,",
    "które posiadają bardziej wyraziste cechy muzyczne.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a markdown report from results/*.txt and results/*.json.")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--template", type=Path, default=Path("templates/report.md.j2"))
    parser.add_argument("--output", type=Path, default=Path("results/generated_report.md"))
    return parser.parse_args()


def parse_clamp3_table(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    generated_at = None
    rows = []

    for line in lines:
        if line.startswith("Wygenerowano:"):
            generated_at = line.split(":", 1)[1].strip()
            continue
        if not line or line.startswith("=") or line.startswith("-"):
            continue
        if line.startswith("CLaMP3 Evaluation"):
            continue
        if line.startswith(("Srednia:", "Min:", "Maks:")):
            continue

        match = re.match(r"^(?P<label>\S+)\s+(?P<score>\d+\.\d+)\s+\((?P<gen>\d+)\s+gen\s+/\s+(?P<ref>\d+)\s+ref\)$", line)
        if match:
            rows.append(
                {
                    "label": match.group("label"),
                    "score": float(match.group("score")),
                    "gen_n": int(match.group("gen")),
                    "ref_n": int(match.group("ref")),
                }
            )

    scores = [row["score"] for row in rows]
    return {
        "generated_at": generated_at,
        "rows": rows,
        "average": mean(scores) if scores else None,
        "min": min(scores) if scores else None,
        "max": max(scores) if scores else None,
    }


def parse_fmd_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def combine_by_label(model_a_rows: list[dict], model_b_rows: list[dict], higher_is_better: bool = True) -> list[dict]:
    model_a = {row["label"]: row for row in model_a_rows}
    model_b = {row["label"]: row for row in model_b_rows}
    labels = sorted(set(model_a) | set(model_b))
    combined = []

    for label in labels:
        left = model_a.get(label)
        right = model_b.get(label)
        left_score = left["score"] if left else None
        right_score = right["score"] if right else None
        delta = None
        winner = "N/A"
        if left_score is not None and right_score is not None:
            delta = left_score - right_score
            if left_score == right_score:
                winner = "Remis"
            elif higher_is_better:
                winner = "MIDI-LLM" if left_score > right_score else "MuseCoco"
            else:
                winner = "MIDI-LLM" if left_score < right_score else "MuseCoco"

        combined.append(
            {
                "label": label,
                "midillm": left_score,
                "musecoco": right_score,
                "delta": delta,
                "winner": winner,
                "midillm_gen_n": left["gen_n"] if left else None,
                "musecoco_gen_n": right["gen_n"] if right else None,
                "midillm_ref_n": left["ref_n"] if left else None,
                "musecoco_ref_n": right["ref_n"] if right else None,
            }
        )

    return combined


def format_metric(value: Optional[float], decimals: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_delta(value: Optional[float], decimals: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.{decimals}f}"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def clamp3_rows_to_table(rows: list[dict]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row["label"],
                format_metric(row["midillm"]),
                format_metric(row["musecoco"]),
                row["winner"],
                format_delta(row["delta"]),
            ]
        )
    return markdown_table(["Kategoria", "MIDI-LLM", "MuseCoco", "Zwycięzca", "Δ"], table_rows)


def fmd_dict_to_table(midillm: dict, musecoco: dict, labels: list[str]) -> str:
    rows = []
    for label in labels:
        left = midillm.get(label)
        right = musecoco.get(label)
        delta = left - right if left is not None and right is not None else None
        winner = "N/A"
        if left is not None and right is not None:
            winner = "MIDI-LLM" if left < right else "MuseCoco"
        rows.append(
            [
                label,
                format_metric(left, 2),
                format_metric(right, 2),
                winner,
                format_delta(delta, 2),
            ]
        )
    return markdown_table(["Kategoria", "MIDI-LLM", "MuseCoco", "Lepszy (niżej)", "Δ"], rows)


def summary_table(clamp3: dict, fmd: dict) -> str:
    rows = [
        ["CLaMP3 per genre", format_metric(clamp3["by_genre"]["midillm_avg"]), format_metric(clamp3["by_genre"]["musecoco_avg"]), format_delta(clamp3["by_genre"]["delta_avg"])],
        ["CLaMP3 per vibe", format_metric(clamp3["by_vibe"]["midillm_avg"]), format_metric(clamp3["by_vibe"]["musecoco_avg"]), format_delta(clamp3["by_vibe"]["delta_avg"])],
        ["CLaMP3 genre × vibe", format_metric(clamp3["genre_vibe"]["midillm_avg"]), format_metric(clamp3["genre_vibe"]["musecoco_avg"]), format_delta(clamp3["genre_vibe"]["delta_avg"])],
        ["FMD genre", format_metric(fmd["genre"]["midillm_avg"], 2), format_metric(fmd["genre"]["musecoco_avg"], 2), format_delta(fmd["genre"]["delta_avg"], 2)],
        ["FMD mood", format_metric(fmd["mood"]["midillm_avg"], 2), format_metric(fmd["mood"]["musecoco_avg"], 2), format_delta(fmd["mood"]["delta_avg"], 2)],
        ["FMD genre-mood", format_metric(fmd["genre_mood"]["midillm_avg"], 2), format_metric(fmd["genre_mood"]["musecoco_avg"], 2), format_delta(fmd["genre_mood"]["delta_avg"], 2)],
    ]
    return markdown_table(["Metryka", "MIDI-LLM", "MuseCoco", "Δ (MIDI-LLM - MuseCoco)"], rows)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_svg(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def grouped_bar_chart_svg(title: str, rows: list[dict], left_key: str, right_key: str, output: Path, lower_is_better: bool = False) -> None:
    width = 1100
    height = 460
    margin_left = 160
    margin_right = 40
    margin_top = 70
    margin_bottom = 120
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    max_val = max([row[left_key] or 0 for row in rows] + [row[right_key] or 0 for row in rows] + [1e-9])
    bar_group_width = plot_width / max(len(rows), 1)
    single_bar = bar_group_width * 0.32

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.small{font-size:12px}.axis{stroke:#4b5563;stroke-width:1}.grid{stroke:#e5e7eb;stroke-width:1}.left{fill:#2563eb}.right{fill:#dc2626}.legend{font-size:13px;font-weight:bold}.title{font-size:20px;font-weight:bold}</style>',
        f'<text class="title" x="{width/2}" y="32" text-anchor="middle">{title}</text>',
    ]

    for tick in range(6):
        value = max_val * tick / 5
        y = margin_top + plot_height - (value / max_val * plot_height if max_val else 0)
        parts.append(f'<line class="grid" x1="{margin_left}" y1="{y}" x2="{width-margin_right}" y2="{y}"/>')
        parts.append(f'<text class="small" x="{margin_left-10}" y="{y+4}" text-anchor="end">{value:.2f}</text>')

    parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top+plot_height}"/>')
    parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top+plot_height}" x2="{width-margin_right}" y2="{margin_top+plot_height}"/>')

    for idx, row in enumerate(rows):
        x_base = margin_left + idx * bar_group_width + bar_group_width * 0.18
        values = [(left_key, "left"), (right_key, "right")]
        for jdx, (key, css) in enumerate(values):
            value = row[key]
            if value is None:
                continue
            bar_height = (value / max_val) * plot_height if max_val else 0
            x = x_base + jdx * (single_bar + 8)
            y = margin_top + plot_height - bar_height
            parts.append(f'<rect class="{css}" x="{x}" y="{y}" width="{single_bar}" height="{bar_height}"/>')
            parts.append(f'<text class="small" x="{x + single_bar/2}" y="{y-6}" text-anchor="middle">{value:.2f}</text>')

        label_x = margin_left + idx * bar_group_width + bar_group_width / 2
        label_y = margin_top + plot_height + 18
        parts.append(f'<g transform="translate({label_x},{label_y}) rotate(40)"><text class="small" text-anchor="start">{row["label"]}</text></g>')

    legend_y = height - 20
    direction = "niżej = lepiej" if lower_is_better else "wyżej = lepiej"
    parts.extend(
        [
            f'<rect class="left" x="{margin_left}" y="{legend_y-12}" width="18" height="12"/>',
            f'<text class="legend" x="{margin_left+26}" y="{legend_y-2}">MIDI-LLM</text>',
            f'<rect class="right" x="{margin_left+140}" y="{legend_y-12}" width="18" height="12"/>',
            f'<text class="legend" x="{margin_left+166}" y="{legend_y-2}">MuseCoco</text>',
            f'<text class="small" x="{width-margin_right}" y="{legend_y-2}" text-anchor="end">{direction}</text>',
        ]
    )
    parts.append("</svg>")
    save_svg(output, "".join(parts))


def heatmap_svg(title: str, matrix: dict[str, dict[str, float]], output: Path) -> None:
    rows = sorted(matrix.keys())
    cols = sorted({col for row in matrix.values() for col in row.keys()})
    cell_w = 92
    cell_h = 42
    margin_left = 130
    margin_top = 90
    width = margin_left + len(cols) * cell_w + 40
    height = margin_top + len(rows) * cell_h + 60

    values = [matrix[row][col] for row in rows for col in cols if col in matrix[row]]
    min_val = min(values) if values else 0
    max_val = max(values) if values else 1

    def color(value: float) -> str:
        if max_val == min_val:
            ratio = 0.5
        else:
            ratio = (value - min_val) / (max_val - min_val)
        red = int(239 - ratio * 180)
        green = int(246 - ratio * 80)
        blue = int(255 - ratio * 140)
        return f"rgb({red},{green},{blue})"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#1f2937}.small{font-size:12px}.title{font-size:20px;font-weight:bold}.label{font-size:13px;font-weight:bold}.cell{stroke:#ffffff;stroke-width:1}</style>',
        f'<text class="title" x="{width/2}" y="30" text-anchor="middle">{title}</text>',
    ]

    for idx, col in enumerate(cols):
        x = margin_left + idx * cell_w + cell_w / 2
        parts.append(f'<g transform="translate({x},70) rotate(-35)"><text class="label" text-anchor="start">{col}</text></g>')

    for row_idx, row in enumerate(rows):
        y = margin_top + row_idx * cell_h
        parts.append(f'<text class="label" x="{margin_left-10}" y="{y + cell_h/2 + 4}" text-anchor="end">{row}</text>')
        for col_idx, col in enumerate(cols):
            x = margin_left + col_idx * cell_w
            value = matrix.get(row, {}).get(col)
            fill = "#f3f4f6" if value is None else color(value)
            label = "" if value is None else f"{value:.3f}"
            parts.append(f'<rect class="cell" x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{fill}"/>')
            parts.append(f'<text class="small" x="{x + cell_w/2}" y="{y + cell_h/2 + 4}" text-anchor="middle">{label}</text>')

    parts.append("</svg>")
    save_svg(output, "".join(parts))


def extract_heatmap(rows: list[dict]) -> dict[str, dict[str, float]]:
    matrix: dict[str, dict[str, float]] = {}
    for row in rows:
        if "/" not in row["label"]:
            continue
        genre, vibe = row["label"].split("/", 1)
        matrix.setdefault(genre, {})[vibe] = row["score"]
    return matrix


def build_context(results_dir: Path, plots_dir: Path) -> dict:
    clamp3_raw = {}
    for model, file_map in CLAMP3_FILES.items():
        clamp3_raw[model] = {
            key: parse_clamp3_table(results_dir / filename)
            for key, filename in file_map.items()
        }

    fmd_raw = {
        model: parse_fmd_json(results_dir / filename)
        for model, filename in FMD_FILES.items()
    }

    by_genre_rows = combine_by_label(
        clamp3_raw["midillm"]["by_genre"]["rows"],
        clamp3_raw["musecoco"]["by_genre"]["rows"],
    )
    by_vibe_rows = combine_by_label(
        clamp3_raw["midillm"]["by_vibe"]["rows"],
        clamp3_raw["musecoco"]["by_vibe"]["rows"],
    )
    genre_vibe_rows = combine_by_label(
        clamp3_raw["midillm"]["genre_vibe"]["rows"],
        clamp3_raw["musecoco"]["genre_vibe"]["rows"],
    )

    midillm_fmd = fmd_raw["midillm"]
    musecoco_fmd = fmd_raw["musecoco"]

    clamp3_summary = {
        "by_genre": {
            "midillm_avg": clamp3_raw["midillm"]["by_genre"]["average"],
            "musecoco_avg": clamp3_raw["musecoco"]["by_genre"]["average"],
            "delta_avg": (clamp3_raw["midillm"]["by_genre"]["average"] or 0) - (clamp3_raw["musecoco"]["by_genre"]["average"] or 0),
        },
        "by_vibe": {
            "midillm_avg": clamp3_raw["midillm"]["by_vibe"]["average"],
            "musecoco_avg": clamp3_raw["musecoco"]["by_vibe"]["average"],
            "delta_avg": (clamp3_raw["midillm"]["by_vibe"]["average"] or 0) - (clamp3_raw["musecoco"]["by_vibe"]["average"] or 0),
        },
        "genre_vibe": {
            "midillm_avg": clamp3_raw["midillm"]["genre_vibe"]["average"],
            "musecoco_avg": clamp3_raw["musecoco"]["genre_vibe"]["average"],
            "delta_avg": (clamp3_raw["midillm"]["genre_vibe"]["average"] or 0) - (clamp3_raw["musecoco"]["genre_vibe"]["average"] or 0),
        },
    }

    fmd_summary = {}
    for key in ("genre", "mood", "genre-mood"):
        mid = midillm_fmd[key]
        mus = musecoco_fmd[key]
        fmd_summary[key.replace("-", "_")] = {
            "midillm_avg": mean(mid.values()),
            "musecoco_avg": mean(mus.values()),
            "delta_avg": mean(mid.values()) - mean(mus.values()),
        }

    grouped_bar_chart_svg("CLaMP3 per genre", by_genre_rows, "midillm", "musecoco", plots_dir / "clamp3_by_genre.svg")
    grouped_bar_chart_svg("CLaMP3 per vibe", by_vibe_rows, "midillm", "musecoco", plots_dir / "clamp3_by_vibe.svg")
    grouped_bar_chart_svg(
        "FMD per genre",
        [
            {"label": label, "midillm": midillm_fmd["genre"].get(label), "musecoco": musecoco_fmd["genre"].get(label)}
            for label in sorted(set(midillm_fmd["genre"]) | set(musecoco_fmd["genre"]))
        ],
        "midillm",
        "musecoco",
        plots_dir / "fmd_by_genre.svg",
        lower_is_better=True,
    )
    grouped_bar_chart_svg(
        "FMD per mood",
        [
            {"label": label, "midillm": midillm_fmd["mood"].get(label), "musecoco": musecoco_fmd["mood"].get(label)}
            for label in sorted(set(midillm_fmd["mood"]) | set(musecoco_fmd["mood"]))
        ],
        "midillm",
        "musecoco",
        plots_dir / "fmd_by_mood.svg",
        lower_is_better=True,
    )
    heatmap_svg("CLaMP3 heatmap — MIDI-LLM", extract_heatmap(clamp3_raw["midillm"]["genre_vibe"]["rows"]), plots_dir / "clamp3_heatmap_midillm.svg")
    heatmap_svg("CLaMP3 heatmap — MuseCoco", extract_heatmap(clamp3_raw["musecoco"]["genre_vibe"]["rows"]), plots_dir / "clamp3_heatmap_musecoco.svg")

    return {
        "generated_from": [
            "results/midillm_by_genre_clamp3.txt",
            "results/midillm_by_vibe_clamp3.txt",
            "results/midillm_genre_vibe_clamp3.txt",
            "results/musecoco_by_genre_clamp3.txt",
            "results/musecoco_by_vibe_clamp3.txt",
            "results/musecoco_genre_vibe_clamp3.txt",
            "results/midillm-scores-v1-1-example.json",
            "results/musecoco-scores-v1.json",
        ],
        "clamp3_by_genre_table": clamp3_rows_to_table(by_genre_rows),
        "clamp3_by_vibe_table": clamp3_rows_to_table(by_vibe_rows),
        "clamp3_genre_vibe_table": clamp3_rows_to_table(genre_vibe_rows),
        "fmd_genre_table": fmd_dict_to_table(midillm_fmd["genre"], musecoco_fmd["genre"], sorted(set(midillm_fmd["genre"]) | set(musecoco_fmd["genre"]))),
        "fmd_mood_table": fmd_dict_to_table(midillm_fmd["mood"], musecoco_fmd["mood"], sorted(set(midillm_fmd["mood"]) | set(musecoco_fmd["mood"]))),
        "summary_table": summary_table(clamp3_summary, fmd_summary),
        "legacy_summary": LEGACY_SUMMARY,
        "plot_paths": {
            "clamp3_by_genre": "plots/clamp3_by_genre.svg",
            "clamp3_by_vibe": "plots/clamp3_by_vibe.svg",
            "clamp3_heatmap_midillm": "plots/clamp3_heatmap_midillm.svg",
            "clamp3_heatmap_musecoco": "plots/clamp3_heatmap_musecoco.svg",
            "fmd_by_genre": "plots/fmd_by_genre.svg",
            "fmd_by_mood": "plots/fmd_by_mood.svg",
        },
        "timestamps": {
            "midillm_genre": clamp3_raw["midillm"]["by_genre"]["generated_at"],
            "musecoco_genre": clamp3_raw["musecoco"]["by_genre"]["generated_at"],
            "midillm_vibe": clamp3_raw["midillm"]["by_vibe"]["generated_at"],
            "musecoco_vibe": clamp3_raw["musecoco"]["by_vibe"]["generated_at"],
            "midillm_genre_vibe": clamp3_raw["midillm"]["genre_vibe"]["generated_at"],
            "musecoco_genre_vibe": clamp3_raw["musecoco"]["genre_vibe"]["generated_at"],
        },
    }


def main() -> None:
    args = parse_args()
    results_dir = args.results_dir.resolve()
    output_path = args.output.resolve()
    template_path = args.template.resolve()
    plots_dir = results_dir / "plots"

    ensure_dir(plots_dir)
    ensure_dir(output_path.parent)

    context = build_context(results_dir, plots_dir)

    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_path.name)
    rendered = template.render(**context)
    output_path.write_text(rendered, encoding="utf-8")

    print(f"Saved report to {output_path}")
    print(f"Saved plots to {plots_dir}")


if __name__ == "__main__":
    main()
