#!/usr/bin/env python3
"""Regenerate descriptive runtime-memory composition evidence.

The complete first-repeat records are exploratory, not an independent release
of the later two-repeat comparison. Sparse variants were not retained for the
second repeat. Components were introduced in bundles, not isolated ablations.
No unused coverage counters, incomplete arms, or inferential tests enter these
outputs. All-outcome summaries and success-conditioned ratios remain separate.
"""

import argparse
import json
import math
import statistics
from pathlib import Path

from build_approach_tables import csv_text, table

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/v-axis/vaxis-trial1.jsonl"
ARMS = ("control", "hybrid-v1", "hybrid-v3", "hybrid-v6", "hybrid-v7")
PREFIX = dict(zip(ARMS, ("Control", "Files", "Commands", "Rich", "Failures")))
LABEL = {
    "control": "Full history",
    "hybrid-v1": "File references",
    "hybrid-v3": "Files, changes, commands",
    "hybrid-v6": "+ diagnostics, environment, tests",
    "hybrid-v7": "+ failed-attempt records",
}
NUMERIC_FIELDS = (
    "turns", "llm_calls", "input_tokens", "cache_read_tokens", "output_tokens",
    "prompt_peak_tokens", "cost_usd",
)


def load_rows(source=SOURCE):
    """Reject malformed or mismatched complete arms; explicitly select scope."""
    with Path(source).open(encoding="utf-8") as handle:
        source_rows = [json.loads(line) for line in handle if line.strip()]
    rows = [row for row in source_rows if row["arm"] in ARMS]
    seen = set()
    tasks = {arm: set() for arm in ARMS}
    for row in rows:
        key = (row["task"], row["arm"], row["trial"])
        if key in seen:
            raise ValueError(f"Duplicate composition record: {key}")
        seen.add(key)
        if row["trial"] != 1 or type(row["solved"]) is not bool:
            raise ValueError(f"Invalid trial or outcome: {key}")
        if row["model"] != "zai/glm-5.3-flash":
            raise ValueError(f"Unexpected model: {key}")
        if row["arm"] != "control":
            if not (row["schema"] == "L2" and row["tail_used"] == 0
                    and row["verified"] is True
                    and row["verified_parts"] == row["arm"].removeprefix("hybrid-")):
                raise ValueError(f"Composition settings differ: {key}")
        for field in NUMERIC_FIELDS:
            value = row[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {field}: {key}")
        normalized_cost = (
            .15 * row["input_tokens"] + .03 * row["cache_read_tokens"] + .50 * row["output_tokens"]
        ) / 1e6
        if not math.isclose(row["cost_usd"], normalized_cost, rel_tol=0, abs_tol=0.000000501):
            raise ValueError(f"Cost disagrees with normalized tariff: {key}")
        tasks[row["arm"]].add(row["task"])
    if not tasks["control"] or any(task_set != tasks["control"] for task_set in tasks.values()):
        raise ValueError("Composition arms do not contain the same complete task set")
    return rows


def summarize(rows):
    cells = {}
    for row in rows:
        cells.setdefault(row["task"], {})[row["arm"]] = row
    fixed = [cell for cell in cells.values() if all(cell[arm]["solved"] for arm in ARMS)]
    if not fixed:
        raise ValueError("No common successful tasks for composition sensitivity analysis")
    summaries = {}
    for arm in ARMS:
        selected = [cell[arm] for cell in cells.values()]
        successes = sum(row["solved"] for row in selected)
        total_cost = math.fsum(row["cost_usd"] for row in selected)
        result = {
            "rate": 100 * successes / len(selected),
            "output_median": statistics.median(row["output_tokens"] for row in selected) / 1000,
            "cost_median": statistics.median(row["cost_usd"] for row in selected),
            "solved_per_dollar": successes / total_cost,
        }
        if arm != "control":
            variable = [cell for cell in cells.values() if cell["control"]["solved"] and cell[arm]["solved"]]
            for name, cohort in (("variable", variable), ("fixed", fixed)):
                for metric, field in (("cost", "cost_usd"), ("turns", "turns"), ("output", "output_tokens")):
                    if any(cell["control"][field] <= 0 for cell in cohort):
                        raise ValueError(f"Zero reference denominator in {name} {metric} ratios")
                    result[f"{name}_{metric}_ratio"] = statistics.median(
                        cell[arm][field] / cell["control"][field] for cell in cohort
                    )
        summaries[arm] = result
    return summaries


def generate(source=SOURCE):
    summaries = summarize(load_rows(source))
    output, macros, main_rows, sensitivity_rows, plot_rows = {}, {}, [], [], []
    metric_contract = (
        ("Rate", "rate", 1), ("OutputMedian", "output_median", 1),
        ("CostMedian", "cost_median", 5), ("SolvedPerDollar", "solved_per_dollar", 2),
        ("VariableCostRatio", "variable_cost_ratio", 2), ("FixedCostRatio", "fixed_cost_ratio", 2),
        ("FixedTurnsRatio", "fixed_turns_ratio", 2), ("FixedOutputRatio", "fixed_output_ratio", 2),
    )
    for order, arm in enumerate(ARMS):
        result = summaries[arm]
        for suffix, field, precision in metric_contract:
            if field in result:
                macros["Explore" + PREFIX[arm] + suffix] = f"{result[field]:.{precision}f}"
        main_rows.append([
            LABEL[arm], f"{result['rate']:.1f}", f"{result['output_median']:.1f}",
            f"{result['cost_median']:.5f}", f"{result['solved_per_dollar']:.2f}",
        ])
        if arm != "control":
            sensitivity_rows.append([LABEL[arm]] + [f"{result[field]:.2f}" + r"$\times$" for field in (
                "variable_cost_ratio", "fixed_cost_ratio", "fixed_turns_ratio", "fixed_output_ratio",
            )])
            plot_rows.append([order - 1, f"{result['rate']:.8f}", f"{result['solved_per_dollar']:.8f}"])
    output["paper/tables/new-composition.tex"] = table(
        ["Runtime-owned information", r"\shortstack{Solved rate\\(\%)}", r"\shortstack{Median output\\(ktok)}",
         r"\shortstack{Median cost\\(\$)}", r"Solved/\$"], main_rows,
    )
    output["paper/tables/new-composition-sensitivity.tex"] = table(
        ["Runtime-owned information", r"\shortstack{Variable subset\\Cost}",
         r"\shortstack{Fixed subset\\Cost}", r"\shortstack{Fixed subset\\Turns}",
         r"\shortstack{Fixed subset\\Output}"], sensitivity_rows,
    )
    output["paper/generated/composition-exploratory.tex"] = (
        "% Generated by analysis/build_composition_exploratory.py; do not edit.\n"
        + "\n".join(rf"\newcommand{{\{key}}}{{{value}}}" for key, value in sorted(macros.items())) + "\n"
    )
    output["paper/generated/new-composition.csv"] = csv_text(
        ["order", "solved_pct", "solved_per_dollar"], plot_rows,
    )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify existing generated artifacts")
    args = parser.parse_args()
    outputs = generate()
    if args.check:
        stale = [path for path, body in outputs.items() if not (ROOT / path).exists() or (ROOT / path).read_text() != body]
        if stale:
            raise SystemExit("Missing or stale exploratory composition artifacts: " + ", ".join(stale))
        print("Exploratory composition artifacts match the complete first-repeat records.")
    else:
        for path, body in outputs.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        print(f"Generated {len(outputs)} exploratory composition artifacts.")


if __name__ == "__main__":
    main()
