"""Numerical and reader-facing contracts for the revised manuscript tables."""

import math
import re
import sys
import csv
import io
import statistics
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
    assert r"Median cost\\(\$)" in history
    assert "0.0137" in history and "0.0154" in history
    assert "0.0104" in history and "0.0144" in history
    assert r"Solved/\$" in history


def test_protocol_price_is_shown_next_to_success(outputs):
    protocol = outputs["paper/tables/new-protocol.tex"]
    assert r"Median cost\\(\$)" in protocol
    assert "39.7" in protocol and "28.7" in protocol
    assert "0.0120" in protocol and "0.0190" in protocol


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


def test_like_comparisons_follow_the_same_two_panel_metric_contract(outputs):
    for comparison in ("history", "runtime", "protocol", "horizon"):
        quality = outputs[f"paper/tables/new-{comparison}.tex"].splitlines()[2]
        resources = outputs[f"paper/tables/new-{comparison}-resources.tex"].splitlines()[2]
        assert quality == " & ".join(tables.QUALITY_HEADERS) + r" \\", comparison
        assert resources == " & ".join(tables.RESOURCE_HEADERS) + r" \\", comparison


def test_cache_hit_uses_per_execution_input_fraction_then_median():
    rows = tables.load_runs()
    summary = tables.model_summary(rows)
    assert tables.cache_hit_pct({"input_tokens": 20, "cache_read_tokens": 80}) == 80
    assert tables.cache_hit_pct({"input_tokens": 0, "cache_read_tokens": 0}) is None
    for arm in tables.MODEL_ARMS:
        selected = [row for row in rows if row["condition"] == arm]
        hits = [100 * row["cache_read_tokens"] / (row["input_tokens"] + row["cache_read_tokens"])
                for row in selected]
        assert summary[arm]["cache_hit_pct"] == statistics.median(hits)
        assert all(abs(hit - row["cache_hit_pct"]) <= 0.051 for hit, row in zip(hits, selected))
    assert summary["baseline"]["cache_hit_pct"] == pytest.approx(83.33838047362364)
    ratio_of_medians = 100 * summary["baseline"]["cache_read_tokens"] / (
        summary["baseline"]["input_tokens"] + summary["baseline"]["cache_read_tokens"])
    assert summary["baseline"]["cache_hit_pct"] != pytest.approx(ratio_of_medians)


def test_no_cache_hit_or_peak_invented_from_final_hybrid_marginal_medians(outputs):
    for row in tables.read_followup().values():
        summary = tables.hybrid_summary(row)
        assert summary["cache_hit_pct"] is None
        assert summary["prompt_peak_tokens"] is None
    for table in ("runtime", "protocol"):
        resources = outputs[f"paper/tables/new-{table}-resources.tex"]
        for line in resources.splitlines():
            if " & " in line and not line.startswith("Approach"):
                assert line.split(" & ")[1] == "--"
                assert line.endswith(r" & -- \\")


def test_all_outcome_cost_ratio_is_distinct_from_joint_success():
    cells = tables.index_by_cell(tables.load_runs())
    ratio = tables.all_outcome_cost_ratio(cells, "tail0")
    expected = statistics.median(cell["tail0"]["cost_usd"] / cell["baseline"]["cost_usd"]
                                 for cell in cells.values())
    assert ratio == expected
    assert ratio != pytest.approx(tables.joint_ratios(cells, "tail0")["cost_usd"])


def test_horizon_membership_is_task_level_and_fixed_by_control_only():
    rows = tables.load_runs()
    actual = tables.horizon_summaries(rows)
    assert [len(tasks) for _, _, tasks, _ in actual] == [31, 29, 27]
    assert [summary["baseline"]["runs"] for _, _, _, summary in actual] == [93, 87, 81]
    changed = [dict(row, turns=999) if row["condition"] != "baseline" else row for row in rows]
    other = tables.horizon_summaries(changed)
    assert [tasks for _, _, tasks, _ in actual] == [tasks for _, _, tasks, _ in other]
    for _, _, tasks, summary in actual:
        assert all(row["runs"] == len(tasks) * 3 for row in summary.values())
    assert actual[-1][3]["tail6"]["cost_ratio_all"] == pytest.approx(0.6648315688161693)


def test_derived_csv_matches_reader_summaries_and_has_no_aggregate_hybrid_rows(outputs):
    summary = list(csv.DictReader(io.StringIO(outputs["paper/generated/model-metric-summary.csv"])))
    assert len(summary) == 16
    assert {row["arm"] for row in summary} == set(tables.MODEL_ARMS)
    assert {row["cohort"] for row in summary} == {"all", "short", "medium", "long"}
    plot = list(csv.DictReader(io.StringIO(outputs["paper/generated/horizon-metrics.csv"])))
    assert len(plot) == 12
    for row in plot:
        matching = next(item for item in summary if item["arm"] == row["arm"] and
                        item["cohort"] == ("short", "medium", "long")[int(row["cohort_order"])])
        assert float(row["cache_hit_pct"]) == float(matching["cache_hit_pct"])


def test_explicit_contrast_tables_preserve_unrounded_tests(outputs):
    contrasts = outputs["paper/tables/new-contrasts.tex"]
    assert "Hybrid variants vs. hybrid state" in contrasts
    assert "[-34.1, -18.8]" in contrasts
    assert "10^{" in contrasts
    assert "0.000" not in contrasts
    assert outputs["paper/tables/new-horizon-contrasts.tex"].count("control median") == 3


def test_generation_is_deterministic(outputs):
    assert tables.generate() == outputs
