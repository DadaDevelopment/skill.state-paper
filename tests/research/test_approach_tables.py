"""Numerical and reader-facing contracts for the revised manuscript tables."""

import math
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))
import build_approach_tables as tables  # noqa: E402


@pytest.fixture(scope="module")
def outputs():
    return tables.generate()


def test_final_followup_margins_are_not_the_old_trial_only_release():
    followup = tables.read_followup()
    assert set(followup) == {
        "control", "hybrid-v6", "hybrid-v7", "hybrid-v7-fit",
        "hybrid-v7-inline", "hybrid-v7-paperlike", "hybrid-v7-tail2", "hybrid-v7-tail6",
    }
    assert {arm: row["solved"] for arm, row in followup.items()} == {
        "control": 90, "hybrid-v6": 67, "hybrid-v7": 69, "hybrid-v7-fit": 72,
        "hybrid-v7-inline": 61, "hybrid-v7-paperlike": 50,
        "hybrid-v7-tail2": 71, "hybrid-v7-tail6": 84,
    }
    assert all(row["repeats"] == 2 for row in followup.values())
    assert math.isclose(sum(row["total_cost_usd_rounded"] for row in followup.values()), 30.76)


def test_model_data_have_separate_reference_and_denominator():
    summary = tables.model_summary(tables.load_runs())
    assert {arm: row["solved"] for arm, row in summary.items()} == {
        "baseline": 160, "tail0": 91, "tail2": 118, "tail6": 154,
    }
    assert all(row["runs"] == 261 for row in summary.values())
    assert math.isclose(summary["baseline"]["cost_total"], 17.851509)


def test_ratios_are_medians_of_matched_ratios_not_ratios_of_medians():
    cells = tables.index_by_cell(tables.load_runs())
    actual = tables.joint_ratios(cells, "tail0")
    assert actual["cost_usd"] == pytest.approx(2.5718161690543977)
    assert actual["prompt_peak_tokens"] == pytest.approx(0.4694921771890672)
    assert actual["input_tokens"] == pytest.approx(1.8633984921530353)
    assert actual["output_tokens"] == pytest.approx(4.554952212082752)
    assert actual["cache_read_tokens"] == pytest.approx(0.8913299541665309)


def test_reference_tests_are_exact_and_nonzero():
    assert tables.mcnemar_exact(0, 0) == 1
    assert tables.mcnemar_exact(2, 0) == pytest.approx(0.5)
    assert tables.mcnemar_exact(3, 3) == pytest.approx(1.0)
    assert tables.mcnemar_exact(82, 13) > 0
    assert "10^{-" in tables.p_tex(tables.mcnemar_exact(82, 13))
    assert tables.p_tex(0.00001) != "0.000"


def test_reader_tables_are_english_and_approach_centered(outputs):
    for filename, body in outputs.items():
        if not filename.startswith("paper/tables/"):
            continue
        assert not re.search(r"\b(?:E1|V.axis|rung|pairs|runs)\b", body, re.IGNORECASE), filename
        assert not re.search(r"[А-Яа-яЁё]", body), filename
        assert not re.search(r"(?<![\d.])(?:87|174|261|1044|1392)(?![\d.])", body), filename
        assert "Control only" not in body
        assert "Solved/runs" not in body
        assert body.startswith(r"\begin{tabular}")
        assert body.rstrip().endswith(r"\end{tabular}")


def test_history_panels_keep_both_references(outputs):
    history = outputs["paper/tables/new-history.tex"]
    assert history.count("Full history") == 2
    assert "61.3" in history and "51.7" in history
    assert "Model-written memory" in history and "Hybrid memory" in history


def test_macros_use_task_bundle_bootstrap_intervals(outputs):
    macros = outputs["paper/generated/approaches.tex"]
    assert r"\newcommand{\ModelStateDeltaCI}{[-34.1, -18.8]}" in macros
    assert r"\newcommand{\ModelHistoryTwoDeltaCI}{[-23.4, -8.8]}" in macros
    assert r"\newcommand{\ModelHistorySixDeltaCI}{[-7.7, +3.4]}" in macros
    assert r"\newcommand{\ProtocolSchemaInteraction}{-8.0}" in macros
    assert "HybridDeltaCI" not in macros


def test_unavailable_hybrid_token_efficiency_is_not_invented(outputs):
    body = outputs["paper/tables/new-economics.tex"].split("Hybrid memory")[1]
    assert body.count(" & --") == 7


def test_generation_is_deterministic(outputs):
    assert tables.generate() == outputs
