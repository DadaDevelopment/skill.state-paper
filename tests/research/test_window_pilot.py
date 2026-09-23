"""Aggregate recovery must not manufacture missing pilot estimands."""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))
import build_approach_tables as approaches
import build_window_pilot as pilot


def test_full_reported_window_axis_is_preserved():
    rows = pilot.extract_tables(pilot.TABLE_SOURCE.read_text())
    assert tuple(rows) == pilot.ARMS
    assert all(row["runs"] == 36 and row["tasks"] == 12 and row["trials"] == 3 for row in rows.values())
    assert [row["cost_median"] for row in rows.values()] == [.0035, .0099, .0054, .0070, .0059, .0060]
    assert [row["calls_median"] for row in rows.values()] == [12, 25, 15, 12, 9, 10]
    assert [row["cache_hit_reported_median_pct"] for row in rows.values()] == [86.5, 64.3, 48.8, 27.1, 27.0, 38.2]
    assert rows["tailinf"]["peak_prompt_median"] == 14018
    assert "State" in pilot.LABELS["tailinf"]
    assert pilot.LABELS["tailinf"] != pilot.LABELS["baseline"]


def test_missing_raw_estimands_are_not_inferred_from_reported_medians():
    rows = pilot.extract_tables(pilot.TABLE_SOURCE.read_text())
    for row in rows.values():
        for field in ("solved_pct", "solved_per_dollar", "uncached_input_median",
                      "cached_input_median", "pooled_matched_cost_ratio"):
            assert row[field] is None
    quality = pilot.generate()["paper/tables/new-window-quality.tex"]
    assert quality.count("--") == 18


def test_final_repeat_ratios_override_partial_log_snapshot():
    rows = pilot.extract_tables(pilot.TABLE_SOURCE.read_text())
    assert [x[0] for x in rows["tailinf"]["cost_ratios"]] == [1.96, 2.00, 1.55]
    assert [x[0] for x in rows["tailinf"]["peak_prompt_ratios"]] == [1.40, 1.69, 1.31]
    assert [x[0] for x in rows["tail12"]["cost_ratios"]] == [2.25, 1.58, 1.63]
    assert rows["tail0"]["cost_ratios"][0] == (2.35, 1.28, 2.97)


def test_repetition_uses_descriptive_medians_without_pseudoreplicated_test():
    medians = pilot.extract_repetition(pilot.REPETITION_SOURCE.read_text())
    assert list(medians.values()) == [1., 1.27, 1.06, 1., 1., 1.]
    table = pilot.generate()["paper/tables/new-window-repetition.tex"]
    assert "higher" not in table and "$p$" not in table
    assert "0.33" not in table


@pytest.mark.parametrize("before,after", [
    ("State + 12 msgs           36", "State + 12 msgs           35"),
    ("Independent trials   3", "Independent trials   2"),
    ("2.25 [1.35-3.43]", "2.25 [2.50-3.43]"),
    ("38.2", "138.2"),
])
def test_changed_or_incomplete_aggregate_sources_fail_closed(before, after):
    text = pilot.TABLE_SOURCE.read_text()
    assert before in text
    with pytest.raises(ValueError):
        pilot.extract_tables(text.replace(before, after))


def test_shared_metric_contract_and_reader_facing_labels():
    outputs = pilot.generate()
    assert " & ".join(approaches.QUALITY_HEADERS) in outputs["paper/tables/new-window-quality.tex"]
    assert " & ".join(approaches.RESOURCE_HEADERS) in outputs["paper/tables/new-window-resources.tex"]
    assert "WindowTwelveCostRatioMin" in outputs["paper/generated/window-pilot.tex"]
    assert "WindowInfiniteCacheHit" in outputs["paper/generated/window-pilot.tex"]
    for path, body in outputs.items():
        if path.startswith("paper/tables/"):
            assert not re.search(r"\b(?:tail\d+|tailinf|E1|V.axis|rung|pairs|runs)\b", body, re.I)
            assert not re.search(r"[А-Яа-яЁё]", body)
    assert pilot.generate() == outputs


def test_check_mode_detects_missing_and_stale_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["build_window_pilot.py", "--check"])
    with pytest.raises(SystemExit, match="Missing or stale"):
        pilot.main()
    monkeypatch.setattr(sys, "argv", ["build_window_pilot.py"])
    pilot.main()
    monkeypatch.setattr(sys, "argv", ["build_window_pilot.py", "--check"])
    pilot.main()
    (tmp_path / "paper/tables/new-window-quality.tex").write_text("stale")
    with pytest.raises(SystemExit, match="Missing or stale"):
        pilot.main()


def test_log_task_outcomes_show_ceiling_from_six_messages():
    outcomes = pilot.extract_log_outcomes(pilot.LOG_OUTCOME_SOURCE.read_text())
    solved = [int(outcomes[arm]["tasks_solved_any_repeat"]) for arm in pilot.ARMS]
    assert solved == [11, 9, 9, 12, 12, 12]
    assert all(int(outcomes[arm]["tasks"]) == 12 for arm in pilot.ARMS)
    table = pilot.generate()["paper/tables/new-window-tasks.tex"]
    assert "100.0" in table and "0/2" in table


def test_log_outcomes_reject_inconsistent_discordant_counts():
    text = pilot.LOG_OUTCOME_SOURCE.read_text().replace("tail6,12,12,1,0", "tail6,12,12,0,0")
    with pytest.raises(ValueError, match="Discordant"):
        pilot.extract_log_outcomes(text)
