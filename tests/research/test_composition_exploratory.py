"""Evidence and estimand contracts for the restored exploratory comparison."""

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))
import build_approach_tables as approaches  # noqa: E402
import build_composition_exploratory as composition  # noqa: E402


@pytest.fixture(scope="module")
def rows():
    return composition.load_rows()


def test_complete_composition_records_are_not_incomplete_protocol_arms(rows):
    assert len(rows) == 435
    assert set(row["arm"] for row in rows) == set(composition.ARMS)
    assert len({row["task"] for row in rows}) == 87
    assert all(row["trial"] == 1 for row in rows)


def test_overlapping_rows_agree_with_final_first_repeat_margins(rows):
    followup = approaches.read_followup()
    for arm in ("control", "hybrid-v6", "hybrid-v7"):
        selected = [row for row in rows if row["arm"] == arm]
        assert sum(row["solved"] for row in selected) == followup[arm]["solved_t1"]
        assert len(selected) == followup[arm]["tasks"]


def test_all_outcome_rates_and_efficiency_use_completed_episodes(rows):
    summaries = composition.summarize(rows)
    assert [round(summaries[arm]["rate"], 1) for arm in composition.ARMS] == [55.2, 28.7, 40.2, 42.5, 41.4]
    assert [round(summaries[arm]["output_median"], 1) for arm in composition.ARMS] == [16.4, 23.2, 16.5, 19.1, 18.6]
    assert [round(summaries[arm]["solved_per_dollar"], 2) for arm in composition.ARMS] == [22.39, 12.87, 20.79, 20.92, 21.19]
    assert summaries["control"]["cost_median"] == pytest.approx(.011392)
    assert summaries["hybrid-v1"]["cost_median"] == pytest.approx(.014065)


def test_common_success_intersection_changes_cost_estimand(rows):
    summaries = composition.summarize(rows)
    arms = composition.ARMS[1:]
    assert [round(summaries[arm]["variable_cost_ratio"], 2) for arm in arms] == [2.31, 1.20, .92, .94]
    assert [round(summaries[arm]["fixed_cost_ratio"], 2) for arm in arms] == [2.50, 1.07, 1.03, 1.17]
    assert [round(summaries[arm]["fixed_turns_ratio"], 2) for arm in arms] == [1.61, .77, .75, .79]
    assert [round(summaries[arm]["fixed_output_ratio"], 2) for arm in arms] == [4.03, 1.56, 1.75, 1.73]


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "trial", "nan", "settings", "tariff"])
def test_invalid_source_records_are_rejected(tmp_path, rows, mutation):
    altered = [dict(row) for row in rows]
    if mutation == "duplicate":
        altered.append(dict(altered[0]))
    elif mutation == "missing":
        altered.pop(0)
    elif mutation == "trial":
        altered[0]["trial"] = 2
    elif mutation == "nan":
        altered[0]["cost_usd"] = float("nan")
    elif mutation == "settings":
        next(row for row in altered if row["arm"] == "hybrid-v1")["tail_used"] = 6
    elif mutation == "tariff":
        altered[0]["cost_usd"] += .01
    source = tmp_path / "invalid.jsonl"
    source.write_text("\n".join(json.dumps(row) for row in altered), encoding="utf-8")
    with pytest.raises(ValueError):
        composition.load_rows(source)


def test_tables_are_english_descriptive_and_readable():
    outputs = composition.generate()
    for path, body in outputs.items():
        if not path.startswith("paper/tables/"):
            continue
        assert not re.search(r"\b(?:v[0-9]+|E1|V.axis|rung|pairs|runs)\b", body, re.IGNORECASE)
        assert not re.search(r"[А-Яа-яЁё]", body)
        assert not re.search(r"(?<![\d.])(?:87|174|261|435)(?![\d.])", body)
        assert "$p$" not in body
    assert "Fixed subset" in outputs["paper/tables/new-composition-sensitivity.tex"]
    assert "Variable subset" in outputs["paper/tables/new-composition-sensitivity.tex"]
    assert composition.generate() == outputs


def test_check_mode_detects_missing_and_stale_generated_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(composition, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["build_composition_exploratory.py", "--check"])
    with pytest.raises(SystemExit, match="Missing or stale"):
        composition.main()
    monkeypatch.setattr(sys, "argv", ["build_composition_exploratory.py"])
    composition.main()
    for path, body in composition.generate().items():
        assert (tmp_path / path).read_text(encoding="utf-8") == body, path
    monkeypatch.setattr(sys, "argv", ["build_composition_exploratory.py", "--check"])
    composition.main()
    (tmp_path / "paper/tables/new-composition.tex").write_text("stale", encoding="utf-8")
    with pytest.raises(SystemExit, match="Missing or stale"):
        composition.main()
