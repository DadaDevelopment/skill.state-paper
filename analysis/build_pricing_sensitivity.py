#!/usr/bin/env python3
"""Reconstruct the log's input-only cache-discount proxy, not author costs."""

import argparse
import csv
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/pricing-sensitivity/source.json"
HORIZONS = (10, 25, 50, 100, 200)
NAMES = ("Ten", "TwentyFive", "Fifty", "Hundred", "TwoHundred")


def load_source(source=SOURCE):
    with Path(source).open(encoding="utf-8") as handle:
        evidence = json.load(handle)
    if evidence.get("direction") != "full_history_over_state":
        raise ValueError("Pricing scenario must preserve full-history/state direction")
    if evidence.get("estimand") != "input_only_discounted_total_token_proxy":
        raise ValueError("Scenario is a discounted-token proxy, not monetary cost")
    scenario = evidence["scenario"]
    for key in ("full_history_hit", "state_hit", "cache_to_input_price"):
        value = scenario[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Invalid scenario fraction: {key}")
    rows = evidence["rows"]
    if tuple(row["horizon"] for row in rows) != HORIZONS:
        raise ValueError("Expected all five published event horizons in order")
    for row in rows:
        for key in ("full_history_total_tokens", "state_total_tokens"):
            if type(row[key]) is not int or row[key] <= 0:
                raise ValueError(f"Invalid published token mean: {key}")
    if discount(scenario["state_hit"], scenario["cache_to_input_price"]) <= 0:
        raise ValueError("State discount produces a zero denominator")
    return evidence


def discount(hit, price_ratio):
    return 1 - hit + price_ratio * hit


def calculate(evidence):
    scenario = evidence["scenario"]
    factor = discount(scenario["full_history_hit"], scenario["cache_to_input_price"]) / discount(
        scenario["state_hit"], scenario["cache_to_input_price"]
    )
    return [
        {
            "horizon": row["horizon"],
            "token_ratio": row["full_history_total_tokens"] / row["state_total_tokens"],
            "proxy_ratio": row["full_history_total_tokens"] / row["state_total_tokens"] * factor,
        }
        for row in evidence["rows"]
    ]


def generate(source=SOURCE):
    evidence = load_source(source)
    rows = calculate(evidence)
    lines = [
        r"\begin{tabular}{@{}rrr@{}}",
        r"\toprule",
        r"\shortstack{Event horizon\\($T$)} & \shortstack{Published token ratio\\(Full / State)} & \shortstack{Discounted-token proxy\\(Full / State)} \\",
        r"\midrule",
    ]
    macros = ["% Generated historical sensitivity scenario; NOT observed monetary cost."]
    for name, row in zip(NAMES, rows):
        lines.append(f"{row['horizon']} & {row['token_ratio']:.2f}" + r"$\times$ & " + f"{row['proxy_ratio']:.2f}" + r"$\times$ \\")
        macros.append(rf"\newcommand{{\OriginalProxy{name}Ratio}}{{{row['proxy_ratio']:.2f}}}")
        macros.append(rf"\newcommand{{\OriginalToken{name}Ratio}}{{{row['token_ratio']:.2f}}}")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("event_horizon", "published_total_token_ratio", "discounted_token_proxy_ratio"))
    writer.writerows((r["horizon"], f"{r['token_ratio']:.10f}", f"{r['proxy_ratio']:.10f}") for r in rows)
    return {
        "paper/tables/new-pricing-sensitivity.tex": "\n".join(lines) + "\n",
        "paper/generated/pricing-sensitivity.tex": "\n".join(macros) + "\n",
        "paper/generated/new-pricing-sensitivity.csv": stream.getvalue(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = generate()
    if args.check:
        stale = [path for path, body in outputs.items() if not (ROOT / path).exists() or (ROOT / path).read_text(encoding="utf-8") != body]
        if stale:
            raise SystemExit("Missing or stale pricing sensitivity artifacts: " + ", ".join(stale))
        print("Pricing sensitivity artifacts match their explicit scenario assumptions.")
    else:
        for path, body in outputs.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        print(f"Generated {len(outputs)} pricing sensitivity artifacts.")


if __name__ == "__main__":
    main()
