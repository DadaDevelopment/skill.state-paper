#!/usr/bin/env python3
"""Recover the complete history-window pilot from its finalized source tables.

This is a deterministic extraction of published aggregates, not a recreation
of absent episode records. In particular, a median of repeat medians is not
the pooled matched-run cost ratio, and task-level any-success counts from an
earlier log are not per-run solved rates. Unavailable estimands stay missing.
"""

import argparse
import hashlib
import re
from pathlib import Path

from build_approach_tables import QUALITY_HEADERS, RESOURCE_HEADERS, csv_text, table

ROOT = Path(__file__).resolve().parents[1]
TABLE_SOURCE = ROOT / "results/TABLES.txt"
REPETITION_SOURCE = ROOT / "results/RESULT-redundant-work.md"
LOG_OUTCOME_SOURCE = ROOT / "data/pilot-window/log-task-outcomes.csv"
ARMS = ("baseline", "tail0", "tail2", "tail6", "tail12", "tailinf")
SOURCE_LABELS = {
    "baseline": "Transcript (control)", "tail0": "State-only",
    "tail2": "State + 2 msgs", "tail6": "State + 6 msgs",
    "tail12": "State + 12 msgs", "tailinf": "State + transcript",
}
LABELS = {
    "baseline": "Full history", "tail0": "Model-written state",
    "tail2": "State + history ($k=2$)", "tail6": "State + history ($k=6$)",
    "tail12": "State + history ($k=12$)",
    "tailinf": r"State + history ($k=\infty$)",
}
PREFIXES = dict(zip(ARMS, ("Control", "State", "Two", "Six", "Twelve", "Infinite")))
METRICS = {
    "peak_prompt": "Peak prompt tokens (ratio to control; 1.00 = same as control)",
    "cost": "Cost (USD) (ratio to control; 1.00 = same as control)",
    "output": "Output tokens (ratio to control; 1.00 = same as control)",
    "calls": "Model calls (ratio to control; 1.00 = same as control)",
}


def extract_tables(text):
    """Parse final absolute medians and each within-repeat ratio/IQR exactly."""
    absolute = text.split("TABLE 2. Absolute measurements per condition", 1)
    if len(absolute) != 2:
        raise ValueError("Missing or changed absolute-measurement table")
    metadata = re.search(r"Task set\s+(\d+) tasks.*?Independent trials\s+(\d+)",
                         text, re.S)
    if not metadata:
        raise ValueError("Missing pilot task/trial metadata")
    task_count, trial_count = map(int, metadata.groups())
    if trial_count != 3:
        raise ValueError("Expected the finalized three-repeat pilot")
    rows = {}
    for arm in ARMS:
        label = re.escape(SOURCE_LABELS[arm])
        matches = re.findall(
            rf"^\s*{label}\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s*$",
            absolute[1], re.M,
        )
        if len(matches) != 1:
            raise ValueError(f"Expected one finalized absolute row for {arm}")
        count, peak, output, cost, calls, hit = matches[0]
        if int(count) != task_count * trial_count:
            raise ValueError(f"Incomplete condition: {arm}")
        rows[arm] = {
            "runs": int(count), "tasks": task_count, "trials": trial_count,
            "peak_prompt_median": int(peak.replace(",", "")),
            "output_median": int(output.replace(",", "")),
            "cost_median": float(cost), "calls_median": int(calls),
            "cache_hit_reported_median_pct": float(hit),
            "solved_pct": None, "uncached_input_median": None,
            "cached_input_median": None, "pooled_matched_cost_ratio": None,
            "solved_per_dollar": None,
        }
        if not 0 <= rows[arm]["cache_hit_reported_median_pct"] <= 100:
            raise ValueError(f"Invalid cache percentage: {arm}")
    for metric, heading in METRICS.items():
        if heading not in absolute[0]:
            raise ValueError(f"Missing ratio panel: {metric}")
        panel = absolute[0].split(heading, 1)[1].split("\n\n", 1)[0]
        for arm in ARMS[1:]:
            pattern = rf"^\s*{re.escape(SOURCE_LABELS[arm])}\s+(.+)$"
            matching = re.findall(pattern, panel, re.M)
            if len(matching) != 1:
                raise ValueError(f"Missing or duplicate {metric} ratio row for {arm}")
            triples = re.findall(r"([\d.]+) \[([\d.]+)-([\d.]+)\]", matching[0])
            if len(triples) != trial_count:
                raise ValueError(f"Incomplete repeat ratio row for {arm}/{metric}")
            rows[arm][f"{metric}_ratios"] = [tuple(map(float, values)) for values in triples]
            for median, lower, upper in rows[arm][f"{metric}_ratios"]:
                if not 0 < lower <= median <= upper:
                    raise ValueError(f"Invalid IQR for {arm}/{metric}")
    return rows


def extract_repetition(text):
    """Admit descriptive medians only; do not repeat pseudo-independent p-values."""
    pilot = text.split("## Result 1:", 1)[1].split("## Result 2:", 1)[0]
    match = re.search(
        r"Median repetition: control ([\d.]+), state-only ([\d.]+), state\+2 ([\d.]+), and ([\d.]+) for\s+every wider condition",
        pilot,
    )
    if not match:
        raise ValueError("Missing or changed finalized repetition medians")
    control, state, two, wider = map(float, match.groups())
    return dict(zip(ARMS, (control, state, two, wider, wider, wider)))


def extract_log_outcomes(text):
    """Read task-level any-repeat counts transcribed from the research log.

    These are reported, not recomputed: raw pilot sessions are unavailable.
    A task counts as solved when at least one of its three repeats passed.
    """
    lines = text.strip().splitlines()
    header = lines[0].split(",")
    outcomes = {}
    for line in lines[1:]:
        record = dict(zip(header, line.split(",")))
        outcomes[record["arm"]] = record
    if tuple(outcomes) != ARMS:
        raise ValueError("Log outcomes must list every window arm in order")
    for arm, record in outcomes.items():
        solved, tasks = int(record["tasks_solved_any_repeat"]), int(record["tasks"])
        if not 0 <= solved <= tasks:
            raise ValueError(f"Invalid solved count: {arm}")
        if arm != "baseline":
            gained, lost = int(record["only_condition"]), int(record["only_control"])
            control = int(outcomes["baseline"]["tasks_solved_any_repeat"])
            if solved - control != gained - lost:
                raise ValueError(f"Discordant counts do not match margins: {arm}")
    return outcomes


def generate(table_source=TABLE_SOURCE, repetition_source=REPETITION_SOURCE,
             log_outcome_source=LOG_OUTCOME_SOURCE):
    source_text = Path(table_source).read_text(encoding="utf-8")
    repetition_text = Path(repetition_source).read_text(encoding="utf-8")
    rows = extract_tables(source_text)
    repetition = extract_repetition(repetition_text)
    outcomes = extract_log_outcomes(Path(log_outcome_source).read_text(encoding="utf-8"))
    outcome_rows = []
    quality_rows, resource_rows, ratio_rows, repeat_rows, csv_rows, ratios_csv, plot_rows = [], [], [], [], [], [], []
    macros = {}
    for order, arm in enumerate(ARMS):
        row, prefix = rows[arm], "Window" + PREFIXES[arm]
        quality_rows.append([LABELS[arm], "--", str(row["calls_median"]),
                             f"{row['cost_median']:.4f}", "--", "--"])
        resource_rows.append([LABELS[arm], f"{row['peak_prompt_median'] / 1000:.2f}",
                              "--", "--", f"{row['output_median'] / 1000:.2f}",
                              f"{row['cache_hit_reported_median_pct']:.1f}"])
        repeat_rows.append([LABELS[arm], f"{repetition[arm]:.2f}"])
        record = outcomes[arm]
        outcome_rows.append([
            LABELS[arm], f"{100 * int(record['tasks_solved_any_repeat']) / int(record['tasks']):.1f}",
            "--" if arm == "baseline" else f"{record['only_condition']}/{record['only_control']}",
            "--" if arm == "baseline" else record["mcnemar_p"],
            f"{repetition[arm]:.2f}", record["output_tokens_per_turn"],
        ])
        macros[prefix + "TasksSolved"] = record["tasks_solved_any_repeat"]
        macros[prefix + "OutputPerTurn"] = record["output_tokens_per_turn"]
        for suffix, value, precision in (
            ("CostMedian", row["cost_median"], 4), ("CallsMedian", row["calls_median"], 0),
            ("PeakMedian", row["peak_prompt_median"] / 1000, 2),
            ("OutputMedian", row["output_median"] / 1000, 2),
            ("CacheHit", row["cache_hit_reported_median_pct"], 1),
            ("Repetition", repetition[arm], 2),
        ):
            macros[prefix + suffix] = f"{value:.{precision}f}"
        csv_rows.append([arm, row["calls_median"], row["cost_median"],
                         row["peak_prompt_median"], row["output_median"],
                         row["cache_hit_reported_median_pct"], repetition[arm],
                         "", "", "", "", ""])
        if arm != "baseline":
            plot_rows.append([order - 1, arm.removeprefix("tail"),
                              row["cache_hit_reported_median_pct"], row["cost_median"],
                              row["peak_prompt_median"] / 1000, repetition[arm]]
                             + [triple[0] for metric in ("cost", "peak_prompt")
                                for triple in row[f"{metric}_ratios"]])
            ratio_rows.append([LABELS[arm]] + [f"{triple[0]:.2f}" for metric in ("cost", "peak_prompt")
                                                 for triple in row[f"{metric}_ratios"]])
            for metric in METRICS:
                triples = row[f"{metric}_ratios"]
                suffix = {"peak_prompt": "Peak", "cost": "Cost", "output": "Output", "calls": "Calls"}[metric]
                macros[prefix + suffix + "RatioMin"] = f"{min(t[0] for t in triples):.2f}"
                macros[prefix + suffix + "RatioMax"] = f"{max(t[0] for t in triples):.2f}"
                for trial, (median, q25, q75) in enumerate(triples, 1):
                    ratios_csv.append([arm, metric, trial, median, q25, q75])
    macros["WindowTaskCount"] = str(rows["baseline"]["tasks"])
    macros["WindowRepeatCount"] = str(rows["baseline"]["trials"])
    macros["WindowArmCount"] = str(len(ARMS))
    provenance = (
        "source_path,sha256\n"
        + "results/TABLES.txt," + hashlib.sha256(source_text.encode()).hexdigest() + "\n"
        + "results/RESULT-redundant-work.md," + hashlib.sha256(repetition_text.encode()).hexdigest() + "\n"
    )
    return {
        "paper/tables/new-window-quality.tex": table(QUALITY_HEADERS, quality_rows),
        "paper/tables/new-window-resources.tex": table(RESOURCE_HEADERS, resource_rows),
        "paper/tables/new-window-repeat-sensitivity.tex": table(
            ["Approach", r"\shortstack{Cost ratio\\Repeat 1}", r"\shortstack{Cost ratio\\Repeat 2}",
             r"\shortstack{Cost ratio\\Repeat 3}", r"\shortstack{Peak ratio\\Repeat 1}",
             r"\shortstack{Peak ratio\\Repeat 2}", r"\shortstack{Peak ratio\\Repeat 3}"], ratio_rows),
        "paper/tables/new-window-tasks.tex": table(
            ["Approach", r"\shortstack{Tasks solved, \%\\(any repeat)}",
             r"\shortstack{Discordant\\(gain/loss)}", r"\shortstack{McNemar\\$p$}",
             r"\shortstack{Median calls /\\distinct calls}",
             r"\shortstack{Output tok\\per turn}"], outcome_rows),
        "paper/tables/new-window-repetition.tex": table(
            ["Approach", r"\shortstack{Median calls /\\distinct calls}"], repeat_rows),
        "paper/generated/window-pilot.tex": (
            "% Generated by analysis/build_window_pilot.py from finalized aggregates.\n"
            + "\n".join(rf"\newcommand{{\{key}}}{{{value}}}" for key, value in sorted(macros.items())) + "\n"
        ),
        "data/pilot-window/summary.csv": csv_text(
            ["arm", "calls_median", "cost_median_usd_reported", "peak_prompt_median_tokens",
             "output_median_tokens", "cache_hit_reported_median_pct", "repetition_median",
             "solved_pct", "uncached_input_median_tokens", "cached_input_median_tokens",
             "pooled_matched_cost_ratio", "solved_per_dollar"], csv_rows),
        "data/pilot-window/repeat-ratios.csv": csv_text(
            ["arm", "metric", "trial", "median", "q25", "q75"], ratios_csv),
        "data/pilot-window/source-sha256.csv": provenance,
        "paper/generated/new-window-curve.csv": csv_text(
            ["order", "k", "cache_hit_reported_pct", "cost_median_usd", "peak_median_ktok",
             "repetition_median", "cost_ratio_t1", "cost_ratio_t2", "cost_ratio_t3",
             "peak_ratio_t1", "peak_ratio_t2", "peak_ratio_t3"], plot_rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = generate()
    if args.check:
        stale = [path for path, body in outputs.items()
                 if not (ROOT / path).exists() or (ROOT / path).read_text(encoding="utf-8") != body]
        if stale:
            raise SystemExit("Missing or stale pilot-window artifacts: " + ", ".join(stale))
        print("Window pilot artifacts match the finalized source aggregates.")
    else:
        for path, body in outputs.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        print(f"Generated {len(outputs)} pilot-window artifacts.")


if __name__ == "__main__":
    main()
