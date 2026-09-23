#!/usr/bin/env python3
"""Generate the approach-centered manuscript's tables, numbers, and plot data.

Episode-level model-written memory data and supplied final hybrid aggregates
remain distinct throughout. Only reader-facing labels are unified. Resource
ratios condition on joint success; episode summaries and efficiencies include
all retained outcomes. Run-count numerators never enter the reader tables.
"""

import argparse
import csv
import io
import math
import statistics
from collections import defaultdict
from pathlib import Path

from build_paper import index_by_cell, load_runs, mcnemar_exact, sign_test_exact

ROOT = Path(__file__).resolve().parents[1]
FOLLOWUP = ROOT / "data/followup-final/arm-summary.csv"
MODEL_ARMS = ("baseline", "tail0", "tail2", "tail6")
HYBRID_ARMS = ("control", "hybrid-v7", "hybrid-v7-tail2", "hybrid-v7-tail6")
PREFIX = {
    "baseline": "ModelControl", "tail0": "ModelState",
    "tail2": "ModelHistoryTwo", "tail6": "ModelHistorySix",
    "control": "HybridControl", "hybrid-v6": "HybridNoFailure",
    "hybrid-v7": "Hybrid", "hybrid-v7-fit": "TaskAdapted",
    "hybrid-v7-inline": "Inline", "hybrid-v7-paperlike": "InlineAdapted",
    "hybrid-v7-tail2": "HybridHistoryTwo", "hybrid-v7-tail6": "HybridHistorySix",
}
LABEL = {
    "baseline": "Full history", "control": "Full history",
    "tail0": "Model-written state", "tail2": "State + history ($k=2$)",
    "tail6": "State + history ($k=6$)",
    "hybrid-v6": "Hybrid, no failure records", "hybrid-v7": "Hybrid state",
    "hybrid-v7-fit": "Hybrid + adapted schema", "hybrid-v7-inline": "Hybrid + inline",
    "hybrid-v7-paperlike": "Hybrid + inline + adapted schema",
    "hybrid-v7-tail2": "Hybrid + history ($k=2$)",
    "hybrid-v7-tail6": "Hybrid + history ($k=6$)",
}
HORIZON_CUTOFF = 11


def p_tex(value):
    """Never round a nonzero p-value to zero."""
    if value >= 0.001:
        return f"{value:.3f}"
    mantissa, exponent = f"{value:.1e}".split("e")
    return rf"${mantissa}\times10^{{{int(exponent)}}}$"


def table(headers, rows, spec=None):
    spec = spec or "@{}l" + "r" * (len(headers) - 1) + "@{}"
    lines = [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    for row in rows:
        if isinstance(row, str):
            lines.append(row)
        else:
            lines.append(" & ".join(str(x) for x in row) + r" \\")
    return "\n".join(lines + [r"\bottomrule", r"\end{tabular}"]) + "\n"


def panel(label, columns):
    return rf"\multicolumn{{{columns}}}{{@{{}}l}}{{\textit{{{label}}}}} \\[2pt]"


def read_followup():
    with FOLLOWUP.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    result = {}
    for source in records:
        row = dict(source)
        for name, value in source.items():
            if name.startswith("median_cost") or name.startswith("total_cost"):
                row[name] = float(value)
            elif name not in {"arm", "protocol", "schema"}:
                row[name] = int(value) if value else None
        assert row["arm"] not in result
        assert row["runs"] == row["tasks"] * row["repeats"]
        assert row["solved_t1"] + row["solved_t2"] == row["solved"]
        assert 0 <= row["solved"] <= row["runs"]
        result[row["arm"]] = row
    assert len(result) == 8
    assert len({(r["tasks"], r["repeats"], r["runs"]) for r in result.values()}) == 1
    for arm, row in result.items():
        for reference, arm_key, reference_key in (
            ("control", "arm_only_vs_control", "control_only_vs_arm"),
            ("hybrid-v7", "arm_only_vs_hybrid", "hybrid_only_vs_arm"),
        ):
            if arm == reference or row[arm_key] is None:
                continue
            arm_only, reference_only = row[arm_key], row[reference_key]
            both = result[reference]["solved"] - reference_only
            neither = row["runs"] - both - arm_only - reference_only
            assert min(arm_only, reference_only, both, neither) >= 0
            assert both + arm_only == row["solved"]
    return result


def model_summary(rows):
    result = {}
    for arm in MODEL_ARMS:
        subset = [r for r in rows if r["condition"] == arm]
        solved = sum(r["solved"] for r in subset)
        cost = sum(r["cost_usd"] for r in subset)
        total_tokens = sum(r["input_tokens"] + r["cache_read_tokens"] + r["output_tokens"] for r in subset)
        result[arm] = {
            "runs": len(subset), "solved": solved, "rate": 100 * solved / len(subset),
            "cost_total": cost, "cost_median": statistics.median(r["cost_usd"] for r in subset),
            "cost_mean": cost / len(subset), "cost_per_success": cost / solved,
            "solved_per_dollar": solved / cost, "solved_per_million_tokens": solved / total_tokens * 1e6,
            **{key: statistics.median(r[key] for r in subset) for key in
               ("turns", "input_tokens", "output_tokens", "cache_read_tokens", "prompt_peak_tokens")},
        }
    return result


def discordants(cells, arm):
    b = sum(v["baseline"]["solved"] == 1 and v[arm]["solved"] == 0 for v in cells.values())
    c = sum(v["baseline"]["solved"] == 0 and v[arm]["solved"] == 1 for v in cells.values())
    return b, c


def joint_ratios(cells, arm):
    subset = [v for v in cells.values() if v["baseline"]["solved"] and v[arm]["solved"]]
    metrics = {}
    for metric in ("cost_usd", "prompt_peak_tokens", "input_tokens", "output_tokens", "cache_read_tokens"):
        ratios = [v[arm][metric] / v["baseline"][metric] for v in subset if v["baseline"][metric] > 0]
        metrics[metric] = statistics.median(ratios)
    gt = sum(v[arm]["cost_usd"] > v["baseline"]["cost_usd"] for v in subset)
    lt = sum(v[arm]["cost_usd"] < v["baseline"]["cost_usd"] for v in subset)
    metrics["p_cost"] = sign_test_exact(gt, lt)
    return metrics


def task_bootstrap_intervals(rows):
    """Resample complete task bundles; fixed seed matches the archived reanalysis.

    The optional numpy dependency is already part of the research audit's pandas
    environment. Resampling repeats independently would not preserve task bundles.
    """
    import numpy as np
    by_task = defaultdict(lambda: defaultdict(list))
    for row in rows:
        by_task[row["task_id"]][row["condition"]].append(row["solved"])
    tasks = sorted(by_task)
    matrix = np.array([[np.mean(by_task[task][arm]) for arm in MODEL_ARMS] for task in tasks])
    rng = np.random.default_rng(20260922)
    boot = np.empty((100000, len(MODEL_ARMS)))
    for start in range(0, len(boot), 2000):
        indices = rng.integers(0, len(tasks), size=(min(2000, len(boot) - start), len(tasks)))
        boot[start:start + len(indices)] = matrix[indices].mean(axis=1)
    return {
        arm: tuple(float(x * 100) for x in np.quantile(boot[:, j] - boot[:, 0], [0.025, 0.975]))
        for j, arm in enumerate(MODEL_ARMS)
    }


def csv_text(headers, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue()


def generate():
    rows = load_runs()
    cells = index_by_cell(rows)
    assert len(cells) * len(MODEL_ARMS) == len(rows)
    assert all(set(cell) == set(MODEL_ARMS) for cell in cells.values())
    model = model_summary(rows)
    hybrid = read_followup()
    ratios = {arm: joint_ratios(cells, arm) for arm in MODEL_ARMS[1:]}
    confidence = task_bootstrap_intervals(rows)
    output, macros = {}, {}

    def add(name, headers, body, spec=None):
        output[f"paper/tables/new-{name}.tex"] = table(headers, body, spec)

    for arm, result in model.items():
        prefix = PREFIX[arm]
        macros[prefix + "Rate"] = f"{result['rate']:.1f}"
        macros[prefix + "Delta"] = f"{result['rate'] - model['baseline']['rate']:+.1f}"
        for suffix, key, precision in (("CostMedian", "cost_median", 4), ("CostMean", "cost_mean", 4),
                                      ("CostPerSuccess", "cost_per_success", 4),
                                      ("SolvedPerDollar", "solved_per_dollar", 2),
                                      ("SolvedPerMillionTokens", "solved_per_million_tokens", 3)):
            macros[prefix + suffix] = f"{result[key]:.{precision}f}"
        macros[prefix + "DeltaCI"] = f"[{confidence[arm][0]:+.1f}, {confidence[arm][1]:+.1f}]"
        if arm != "baseline":
            macros[prefix + "P"] = p_tex(mcnemar_exact(*discordants(cells, arm)))
            for suffix, key in (("CostRatio", "cost_usd"), ("PeakRatio", "prompt_peak_tokens"),
                                ("InputRatio", "input_tokens"), ("OutputRatio", "output_tokens"),
                                ("CachedRatio", "cache_read_tokens")):
                macros[prefix + suffix] = f"{ratios[arm][key]:.2f}"

    for arm, result in hybrid.items():
        prefix = PREFIX[arm]
        macros[prefix + "Rate"] = f"{100 * result['solved'] / result['runs']:.1f}"
        macros[prefix + "Delta"] = f"{100 * (result['solved'] - hybrid['control']['solved']) / result['runs']:+.1f}"
        macros[prefix + "VsHybridDelta"] = f"{100 * (result['solved'] - hybrid['hybrid-v7']['solved']) / result['runs']:+.1f}"
        macros[prefix + "CostMedian"] = f"{result['median_cost_usd']:.4f}"
        macros[prefix + "CostMean"] = f"{result['total_cost_usd_rounded'] / result['runs']:.4f}"
        macros[prefix + "CostPerSuccess"] = f"{result['total_cost_usd_rounded'] / result['solved']:.4f}"
        macros[prefix + "SolvedPerDollar"] = f"{result['solved'] / result['total_cost_usd_rounded']:.2f}"
        if arm != "control":
            macros[prefix + "P"] = p_tex(mcnemar_exact(result["arm_only_vs_control"], result["control_only_vs_arm"]))
        if result["arm_only_vs_hybrid"] is not None:
            macros[prefix + "VsHybridP"] = p_tex(mcnemar_exact(result["arm_only_vs_hybrid"], result["hybrid_only_vs_arm"]))

    interaction = 100 * (hybrid["hybrid-v7-paperlike"]["solved"] - hybrid["hybrid-v7-fit"]["solved"]
                         - hybrid["hybrid-v7-inline"]["solved"] + hybrid["hybrid-v7"]["solved"]) / hybrid["control"]["runs"]
    macros["ProtocolSchemaInteraction"] = f"{interaction:+.1f}"
    macros["HistoryHorizonCutoff"] = str(HORIZON_CUTOFF)
    macros["ModelHistorySixVsStateDelta"] = f"{model['tail6']['rate'] - model['tail0']['rate']:+.1f}"
    macros["ModelHistoryTwoVsStateDelta"] = f"{model['tail2']['rate'] - model['tail0']['rate']:+.1f}"

    history = [panel("Model-written memory", 6)]
    for arm, k in zip(MODEL_ARMS, ("--", "0", "2", "6")):
        history.append(["Full history" if arm == "baseline" else "Model-written state", k,
                        f"{model[arm]['rate']:.1f}", macros[PREFIX[arm] + "CostPerSuccess"],
                        "--" if arm == "baseline" else macros[PREFIX[arm] + "Delta"],
                        "--" if arm == "baseline" else macros[PREFIX[arm] + "P"]])
    history += [r"\midrule", panel("Hybrid memory", 6)]
    for arm, k in zip(HYBRID_ARMS, ("--", "0", "2", "6")):
        history.append(["Full history" if arm == "control" else "Hybrid state", k, macros[PREFIX[arm] + "Rate"],
                        macros[PREFIX[arm] + "CostPerSuccess"],
                        "--" if arm == "control" else macros[PREFIX[arm] + "Delta"],
                        "--" if arm == "control" else macros[PREFIX[arm] + "P"]])
    add("history", ["Approach", "$k$", r"\shortstack{Solved rate\\(\%)}",
                    r"\shortstack{Cost/success\\(\$)}", r"$\Delta$ (pp)", "$p$"], history)

    runtime = []
    for arm in ("control", "hybrid-v6", "hybrid-v7"):
        result = hybrid[arm]
        runtime.append([LABEL[arm], macros[PREFIX[arm] + "Rate"], f"{result['median_output_tokens'] / 1000:.1f}",
                        f"{result['median_cache_read_tokens'] / 1000:.1f}", f"{result['median_cost_usd']:.4f}",
                        "--" if arm == "control" else macros[PREFIX[arm] + "P"]])
    add("runtime", ["Approach", r"\shortstack{Solved rate\\(\%)}", r"\shortstack{Output\\(ktok)}", r"\shortstack{Cached\\(ktok)}", r"\shortstack{Median cost\\(\$)}", "$p$"], runtime)

    protocol = []
    for arm in ("hybrid-v7", "hybrid-v7-inline", "hybrid-v7-fit", "hybrid-v7-paperlike"):
        result = hybrid[arm]
        protocol.append([result["protocol"].title(), "Existing" if result["schema"] == "existing" else "Task-adapted",
                         macros[PREFIX[arm] + "Rate"], f"{result['median_output_tokens'] / 1000:.1f}",
                         f"{result['median_cost_usd']:.4f}", macros[PREFIX[arm] + "CostPerSuccess"],
                         "--" if arm == "hybrid-v7" else macros[PREFIX[arm] + "VsHybridP"]])
    add("protocol", ["Protocol", "Schema", r"\shortstack{Solved rate\\(\%)}", r"\shortstack{Output\\(ktok)}",
                     r"\shortstack{Median cost\\(\$)}", r"\shortstack{Cost/success\\(\$)}", "$p$"], protocol,
        "@{}llrrrrr@{}")

    resource = []
    for arm in MODEL_ARMS[1:]:
        result = ratios[arm]
        resource.append([LABEL[arm]] + [f"{result[key]:.2f}" + r"$\times$" for key in
                        ("cost_usd", "prompt_peak_tokens", "input_tokens", "output_tokens", "cache_read_tokens")]
                        + [p_tex(result["p_cost"])])
    add("resources", ["Approach", "Cost", "Peak prompt", "Input", "Output", "Cached", "$p$"], resource)

    tokens = []
    for arm in MODEL_ARMS:
        result = model[arm]
        tokens.append([LABEL[arm], f"{result['turns']:g}"] + [f"{result[key] / 1000:.1f}" for key in
                      ("prompt_peak_tokens", "input_tokens", "output_tokens", "cache_read_tokens")])
    add("tokens", ["Approach", r"Median $T$", r"\shortstack{Peak prompt\\(ktok)}", r"\shortstack{Input\\(ktok)}", r"\shortstack{Output\\(ktok)}", r"\shortstack{Cached\\(ktok)}"], tokens)

    economics = [panel("Model-written memory", 5)]
    for arm in MODEL_ARMS:
        result = model[arm]
        economics.append([LABEL[arm], f"{result['cost_median']:.4f}", f"{result['cost_mean']:.4f}",
                          f"{result['solved_per_dollar']:.2f}", f"{result['solved_per_million_tokens']:.3f}"])
    economics += [r"\midrule", panel("Hybrid memory (efficiencies approximate)", 5)]
    for arm in ("control", "hybrid-v7", "hybrid-v7-fit", "hybrid-v7-inline", "hybrid-v7-paperlike",
                "hybrid-v7-tail2", "hybrid-v7-tail6"):
        result = hybrid[arm]
        economics.append([LABEL[arm], macros[PREFIX[arm] + "CostMedian"], macros[PREFIX[arm] + "CostMean"],
                          macros[PREFIX[arm] + "SolvedPerDollar"], "--"])
    add("economics", ["Approach", r"\shortstack{Median cost\\(\$)}", r"\shortstack{Mean cost\\(\$)}", r"Solved/\$", "Solved/Mtok"], economics)

    task_turns = defaultdict(list)
    for row in rows:
        if row["condition"] == "baseline":
            task_turns[row["task_id"]].append(row["turns"])
    strata = [{task for task, turns in task_turns.items() if statistics.median(turns) <= HORIZON_CUTOFF},
              {task for task, turns in task_turns.items() if statistics.median(turns) > HORIZON_CUTOFF}]
    assert len(strata[0] | strata[1]) == len(task_turns) and not strata[0] & strata[1]
    horizon = [r" & \multicolumn{3}{c}{Control median $T\leq" + str(HORIZON_CUTOFF) + r"$} & \multicolumn{3}{c}{Control median $T>" + str(HORIZON_CUTOFF) + r"$} \\",
               r"\cmidrule(lr){2-4}\cmidrule(l){5-7}",
               r"Approach & \shortstack{Solved rate\\(\%)} & $\Delta$ (pp) & $p$ & \shortstack{Solved rate\\(\%)} & $\Delta$ (pp) & $p$ \\", r"\midrule"]
    for arm in MODEL_ARMS:
        row = [LABEL[arm]]
        for tasks in strata:
            selected = {key: value for key, value in cells.items() if key[0] in tasks}
            rate = 100 * sum(cell[arm]["solved"] for cell in selected.values()) / len(selected)
            base_rate = 100 * sum(cell["baseline"]["solved"] for cell in selected.values()) / len(selected)
            row += [f"{rate:.1f}", "--" if arm == "baseline" else f"{rate - base_rate:+.1f}",
                    "--" if arm == "baseline" else p_tex(mcnemar_exact(*discordants(selected, arm)))]
        horizon.append(" & ".join(row) + r" \\")
    output["paper/tables/new-horizon.tex"] = "\n".join([r"\begin{tabular}{@{}lrrrrrr@{}}", r"\toprule"] + horizon + [r"\bottomrule", r"\end{tabular}"]) + "\n"

    output["paper/generated/approaches.tex"] = "% Generated by analysis/build_approach_tables.py; do not edit.\n" + "\n".join(
        rf"\newcommand{{\{key}}}{{{value}}}" for key, value in sorted(macros.items())) + "\n"
    for family, arms in (("model", MODEL_ARMS), ("hybrid", HYBRID_ARMS)):
        plot = []
        for order, arm in enumerate(arms):
            if family == "model":
                rate, mean_cost = model[arm]["rate"], model[arm]["cost_mean"]
            else:
                rate = 100 * hybrid[arm]["solved"] / hybrid[arm]["runs"]
                mean_cost = hybrid[arm]["total_cost_usd_rounded"] / hybrid[arm]["runs"]
            plot.append([order, "full" if order == 0 else ("0", "2", "6")[order - 1], f"{rate:.8f}", f"{mean_cost:.8f}"])
        output[f"paper/generated/new-{family}-history.csv"] = csv_text(["order", "history", "solved_pct", "mean_cost_usd"], plot)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed/generated outputs without changing files")
    args = parser.parse_args()
    outputs = generate()
    if args.check:
        stale = [path for path, body in outputs.items() if not (ROOT / path).exists() or (ROOT / path).read_text() != body]
        if stale:
            raise SystemExit("Missing or stale generated artifacts: " + ", ".join(stale))
        print("Approach tables, macros, and plot data match both independent source releases.")
    else:
        for path, body in outputs.items():
            destination = ROOT / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(body, encoding="utf-8")
        print(f"Generated {len(outputs)} approach-centered artifacts from separate source releases.")


if __name__ == "__main__":
    main()
