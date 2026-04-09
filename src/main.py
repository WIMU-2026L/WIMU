import logging

import data.data_loader as data_loader
from data.midisample_class import MidiSample
from config import BASE_DIR, XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR, LOGS_DIR, TOPK15_REMI_DIR, TOPK15_MIDI_DIR
from metrics.fmd import calculate_fmd,calculate_fmd_inf
from reporting import make_comparison, write_report

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(filename=LOGS_DIR / "app.log", level=logging.INFO)

    # converted_remi_files = data_loader.convert_remi_data(TOPK15_REMI_DIR, TOPK15_MIDI_DIR)
    # print(f"Converted {len(converted_remi_files)} REMI files to MIDI.")


    midi_subset: list[MidiSample] = data_loader.load_data(XMIDI_SUBSET_DIR)
    generated_music: list[MidiSample] = data_loader.load_data(XMIDI_GENERATED_DIR)

    fmd_score = calculate_fmd(XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR)
    logger.info(f"fmd_score : {fmd_score}")
    fmd_score_inf = calculate_fmd_inf(XMIDI_SUBSET_DIR, XMIDI_GENERATED_DIR)
    logger.info(f"fmd_score_inf:{fmd_score_inf}")

    fmd_inf_steps = 25
    fmd_inf_min_n = 2
    genre_pairs = [
        ("pop", XM`IDI_SUBSET_DIR / "pop", TOPK15_MIDI_DIR / "pop"),
        ("jazz", XMIDI_SUBSET_DIR / "jazz", TOPK15_MIDI_DIR / "jazz"),
        ("religious", XMIDI_SUBSET_DIR / "religious", TOPK15_MIDI_DIR / "religious"),
    ]

    comparisons = []
    for genre_name, reference_path, test_path in genre_pairs:
        genre_fmd_score = calculate_fmd(reference_path, test_path)
        genre_fmd_inf = calculate_fmd_inf(reference_path, test_path, steps=fmd_inf_steps, min_n=fmd_inf_min_n)
        logger.info(f"{genre_name}_fmd_score:{genre_fmd_score}")
        logger.info(f"{genre_name}_fmd_score_inf:{genre_fmd_inf}")
        comparisons.append(
            make_comparison(
                reference_genre=genre_name,
                test_genre=genre_name,
                reference_path=reference_path,
                test_path=test_path,
                fmd_score=genre_fmd_score,
                fmd_inf_result=genre_fmd_inf,
            )
        )

    report_path = write_report(
        template_dir=BASE_DIR / "templates",
        template_name="fmd_genre_report.md.j2",
        output_path=BASE_DIR / "reports" / "fmd_genre_report.md",
        title="FMD Genre Comparison Report",
        experiment_name="XMIDI subset vs generated genre folders",
        reference_root=XMIDI_SUBSET_DIR,
        test_root=TOPK15_MIDI_DIR,
        comparisons=comparisons,
        fmd_inf_steps=fmd_inf_steps,
        fmd_inf_min_n=fmd_inf_min_n,
    )
    print(f"Report saved to {report_path}")
