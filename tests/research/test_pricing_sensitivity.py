"""Keep the historical input-only sensitivity separate from empirical cost."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import build_pricing_sensitivity as pricing


def test_exact_source_means_and_assumption_provenance():
    source = pricing.load_source()
    assert source["source_url"] == "https://arxiv.org/html/2608.26263v3#S4.T1"
    assert source["scenario"]["status"] == "historical_log_assumptions_not_final_experiment_statistics"
    assert [r["full_history_total_tokens"] for r in source["rows"]] == [9438, 42689, 171658, 1245413, 2608755]
    assert [r["state_total_tokens"] for r in source["rows"]] == [5870, 14714, 30151, 65408, 122384]
    assert {"authors_monetary_cost", "authors_cache_hit", "output_pricing", "cost_crossover"} <= set(source["not_estimated"])


def test_screenshot_is_reconstructed_as_a_proxy_not_an_invoice():
    rows = pricing.calculate(pricing.load_source())
    assert [r["horizon"] for r in rows] == [10, 25, 50, 100, 200]
    assert [r["proxy_ratio"] for r in rows] == pytest.approx([
        .9670000877268237, 1.7448973034359472, 3.4241041754608577,
        11.451626283221927, 12.820155490515965,
    ])
    for row in rows:
        assert row["proxy_ratio"] / row["token_ratio"] == pytest.approx(.6014293828095417)


@pytest.mark.parametrize("mutation", ["direction", "estimand", "hit", "nan", "missing", "tokens", "zero"])
def test_invalid_sources_fail_loudly(tmp_path, mutation):
    data = pricing.load_source()
    if mutation == "direction":
        data["direction"] = "state_over_full_history"
    elif mutation == "estimand":
        data["estimand"] = "actual_cost"
    elif mutation == "hit":
        data["scenario"]["state_hit"] = 1.01
    elif mutation == "nan":
        data["scenario"]["full_history_hit"] = float("nan")
    elif mutation == "missing":
        data["rows"].pop()
    elif mutation == "tokens":
        data["rows"][0]["state_total_tokens"] = 0
    else:
        data["scenario"]["state_hit"] = 1
        data["scenario"]["cache_to_input_price"] = 0
    path = tmp_path / "source.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        pricing.load_source(path)


def test_artifacts_label_proxy_and_keep_the_ratio_direction():
    outputs = pricing.generate()
    table = outputs["paper/tables/new-pricing-sensitivity.tex"]
    assert "Discounted-token proxy" in table
    assert table.count("Full / State") == 2
    assert "1.74" in table
    assert "USD" not in table and "Cost" not in table and "Solved" not in table
    macros = outputs["paper/generated/pricing-sensitivity.tex"]
    assert r"\OriginalProxyTenRatio}{0.97}" in macros
    assert r"\OriginalProxyFiftyRatio}{3.42}" in macros
    assert pricing.generate() == outputs


def test_check_mode_detects_missing_or_stale_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(pricing, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["build_pricing_sensitivity.py", "--check"])
    with pytest.raises(SystemExit, match="Missing or stale"):
        pricing.main()
    monkeypatch.setattr(sys, "argv", ["build_pricing_sensitivity.py"])
    pricing.main()
    monkeypatch.setattr(sys, "argv", ["build_pricing_sensitivity.py", "--check"])
    pricing.main()
    (tmp_path / "paper/tables/new-pricing-sensitivity.tex").write_text("stale", encoding="utf-8")
    with pytest.raises(SystemExit, match="Missing or stale"):
        pricing.main()
