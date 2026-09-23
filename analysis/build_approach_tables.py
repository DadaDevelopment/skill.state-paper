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
HORIZON_BOUNDS = (8, 20)
QUALITY_HEADERS = ["Approach", r"\shortstack{Solved rate\\(\%)}", r"Median $T$",
                   r"\shortstack{Median cost\\(\$)}", r"\shortstack{Cost ratio\\($\times$)}", r"Solved/\$"]
RESOURCE_HEADERS = ["Approach", r"\shortstack{Peak prompt\\(ktok)}",
                    r"\shortstack{Uncached in\\(ktok)}", r"\shortstack{Cached in\\(ktok)}",
                    r"\shortstack{Output\\(ktok)}", r"\shortstack{Cache hit\\(\%)}"]


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


def cache_hit_pct(row):
    """Per-execution fraction of input tokens served from cache, not output."""
    denominator = row["input_tokens"] + row["cache_read_tokens"]
    return 100 * row["cache_read_tokens"] / denominator if denominator else None


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
            "cache_hit_pct": statistics.median(hit for r in subset if (hit := cache_hit_pct(r)) is not None),
            **{key: statistics.median(r[key] for r in subset) for key in
               ("turns", "input_tokens", "output_tokens", "cache_read_tokens", "prompt_peak_tokens")},
        }
    return result


def all_outcome_cost_ratio(cells, arm):
    """Median matched cost ratio, retaining both solved and unsolved outcomes."""
    assert all(cell["baseline"]["cost_usd"] > 0 for cell in cells.values()), "Zero-cost reference needs an explicit estimand"
    return statistics.median(cell[arm]["cost_usd"] / cell["baseline"]["cost_usd"]
                             for cell in cells.values())


def quality_row(label, summary, cost_ratio=None):
    return [label, f"{summary['rate']:.1f}", f"{summary['turns']:g}",
            f"{summary['cost_median']:.4f}", "--" if cost_ratio is None else f"{cost_ratio:.2f}",
            f"{summary['solved_per_dollar']:.2f}"]


def resource_row(label, summary):
    return [label] + ["--" if summary.get(key) is None else f"{summary[key] / divisor:.1f}"
                     for key, divisor in (("prompt_peak_tokens", 1000), ("input_tokens", 1000),
                                          ("cache_read_tokens", 1000), ("output_tokens", 1000),
                                          ("cache_hit_pct", 1))]


def hybrid_summary(row):
    """Normalize supplied aggregates without inventing unavailable statistics."""
    return {"rate": 100 * row["solved"] / row["runs"], "turns": row["median_turns"],
            "cost_median": row["median_cost_usd"],
            "solved_per_dollar": row["solved"] / row["total_cost_usd_rounded"],
            "input_tokens": row["median_input_tokens"], "output_tokens": row["median_output_tokens"],
            "cache_read_tokens": row["median_cache_read_tokens"],
            "prompt_peak_tokens": None, "cache_hit_pct": None}


def horizon_summaries(rows):
    """Posthoc task cohorts, held fixed across conditions using control length."""
    control_turns = defaultdict(list)
    for row in rows:
        if row["condition"] == "baseline":
            control_turns[row["task_id"]].append(row["turns"])
    medians = {task: statistics.median(turns) for task, turns in control_turns.items()}
    short, medium = HORIZON_BOUNDS
    cohorts = (
        ("Short", rf"Short: control median $T\leq{short}$", {t for t, n in medians.items() if n <= short}),
        ("Medium", rf"Medium: control median ${short}<T\leq{medium}$", {t for t, n in medians.items() if short < n <= medium}),
        ("Long", rf"Long: control median $T>{medium}$", {t for t, n in medians.items() if n > medium}),
    )
    assert set.union(*(cohort[2] for cohort in cohorts)) == set(medians)
    assert sum(len(cohort[2]) for cohort in cohorts) == len(medians)
    result = []
    for name, label, tasks in cohorts:
        selected = [row for row in rows if row["task_id"] in tasks]
        cells = index_by_cell(selected)
        summary = model_summary(selected)
        for arm in MODEL_ARMS:
            summary[arm]["cost_ratio_all"] = all_outcome_cost_ratio(cells, arm)
            summary[arm]["p_vs_control"] = mcnemar_exact(*discordants(cells, arm))
        result.append((name, label, tasks, summary))
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
    hybrid_metrics = {arm: hybrid_summary(row) for arm, row in hybrid.items()}
    all_ratios = {arm: all_outcome_cost_ratio(cells, arm) for arm in MODEL_ARMS}
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
        macros[prefix + "CacheHit"] = f"{result['cache_hit_pct']:.1f}"
        macros[prefix + "AllCostRatio"] = f"{all_ratios[arm]:.2f}"
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
    history_resources = [panel("Model-written memory", 6)]
    for arm in MODEL_ARMS:
        history.append(quality_row(LABEL[arm], model[arm], all_ratios[arm]))
        history_resources.append(resource_row(LABEL[arm], model[arm]))
    history += [r"\midrule", panel("Hybrid memory", 6)]
    history_resources += [r"\midrule", panel("Hybrid memory", 6)]
    for arm in HYBRID_ARMS:
        history.append(quality_row(LABEL[arm], hybrid_metrics[arm]))
        history_resources.append(resource_row(LABEL[arm], hybrid_metrics[arm]))
    add("history", QUALITY_HEADERS, history)
    add("history-resources", RESOURCE_HEADERS, history_resources)

    for name, arms in (
        ("runtime", ("control", "hybrid-v6", "hybrid-v7")),
        ("protocol", ("hybrid-v7", "hybrid-v7-inline", "hybrid-v7-fit", "hybrid-v7-paperlike")),
    ):
        def label(arm):
            if name == "protocol":
                row = hybrid[arm]
                return row["protocol"].title() + " / " + ("Existing" if row["schema"] == "existing" else "Adapted")
            return LABEL[arm]
        add(name, QUALITY_HEADERS, [quality_row(label(arm), hybrid_metrics[arm]) for arm in arms])
        add(name + "-resources", RESOURCE_HEADERS,
            [resource_row(label(arm), hybrid_metrics[arm]) for arm in arms])

    resource = []
    for arm in MODEL_ARMS[1:]:
        result = ratios[arm]
        resource.append([LABEL[arm]] + [f"{result[key]:.2f}" + r"$\times$" for key in
                        ("cost_usd", "prompt_peak_tokens", "input_tokens", "output_tokens", "cache_read_tokens")]
                        + [p_tex(result["p_cost"])])
    add("resources", ["Approach", "Cost", "Peak prompt", "Input", "Output", "Cached", "$p$"], resource)

    add("tokens", RESOURCE_HEADERS, [resource_row(LABEL[arm], model[arm]) for arm in MODEL_ARMS])

    economics = [panel("Model-written memory", 6)]
    for arm in MODEL_ARMS:
        result = model[arm]
        economics.append([LABEL[arm], f"{result['cost_median']:.4f}", f"{result['cost_mean']:.4f}",
                          f"{result['cost_per_success']:.4f}",
                          f"{result['solved_per_dollar']:.2f}", f"{result['solved_per_million_tokens']:.3f}"])
    economics += [r"\midrule", panel("Hybrid memory (efficiencies approximate)", 6)]
    for arm in ("control", "hybrid-v7", "hybrid-v7-fit", "hybrid-v7-inline", "hybrid-v7-paperlike",
                "hybrid-v7-tail2", "hybrid-v7-tail6"):
        result = hybrid[arm]
        economics.append([LABEL[arm], macros[PREFIX[arm] + "CostMedian"], macros[PREFIX[arm] + "CostMean"],
                          macros[PREFIX[arm] + "CostPerSuccess"], macros[PREFIX[arm] + "SolvedPerDollar"], "--"])
    add("economics", ["Approach", r"\shortstack{Median cost\\(\$)}", r"\shortstack{Mean cost\\(\$)}",
                      r"\shortstack{Cost/success\\(\$)}", r"Solved/\$", "Solved/Mtok"], economics)

    contrasts = [panel("Model-written memory vs. full history", 4)]
    for arm in MODEL_ARMS[1:]:
        prefix = PREFIX[arm]
        contrasts.append([LABEL[arm], macros[prefix + "Delta"], macros[prefix + "DeltaCI"], macros[prefix + "P"]])
    contrasts += [r"\midrule", panel("Hybrid memory vs. full history", 4)]
    for arm in hybrid:
        if arm != "control":
            prefix = PREFIX[arm]
            contrasts.append([LABEL[arm], macros[prefix + "Delta"], "--", macros[prefix + "P"]])
    contrasts += [r"\midrule", panel("Hybrid variants vs. hybrid state", 4)]
    for arm, row in hybrid.items():
        if arm != "hybrid-v7" and row["arm_only_vs_hybrid"] is not None:
            prefix = PREFIX[arm]
            contrasts.append([LABEL[arm], macros[prefix + "VsHybridDelta"], "--", macros[prefix + "VsHybridP"]])
    add("contrasts", ["Approach", r"$\Delta$ (pp)", r"95\% CI (pp)", "$p$"], contrasts)

    horizon, horizon_resources, horizon_contrasts, horizon_plot = [], [], [], []
    summary_rows = []
    summary_keys = ("runs", "solved", "rate", "turns", "cost_median", "cost_mean", "cost_per_success",
                    "solved_per_dollar", "prompt_peak_tokens", "input_tokens", "cache_read_tokens",
                    "output_tokens", "cache_hit_pct", "cost_ratio_all")
    for arm in MODEL_ARMS:
        summary = dict(model[arm], cost_ratio_all=all_ratios[arm])
        summary_rows.append(["all", arm] + [summary[key] for key in summary_keys])
    for order, (name, label, tasks, summary) in enumerate(horizon_summaries(rows)):
        if horizon:
            horizon.append(r"\midrule")
            horizon_resources.append(r"\midrule")
            horizon_contrasts.append(r"\midrule")
        horizon.append(panel(label, len(QUALITY_HEADERS)))
        horizon_resources.append(panel(label, len(RESOURCE_HEADERS)))
        horizon_contrasts.append(panel(label, 3))
        macros["Horizon" + name + "Tasks"] = str(len(tasks))
        for arm in MODEL_ARMS:
            result = summary[arm]
            prefix = "Horizon" + name + PREFIX[arm]
            horizon.append(quality_row(LABEL[arm], result, result["cost_ratio_all"]))
            horizon_resources.append(resource_row(LABEL[arm], result))
            delta = result["rate"] - summary["baseline"]["rate"]
            macros[prefix + "Rate"] = f"{result['rate']:.1f}"
            macros[prefix + "Delta"] = f"{delta:+.1f}"
            macros[prefix + "CacheHit"] = f"{result['cache_hit_pct']:.1f}"
            macros[prefix + "CostMedian"] = f"{result['cost_median']:.4f}"
            macros[prefix + "CostPerSuccess"] = f"{result['cost_per_success']:.4f}"
            macros[prefix + "AllCostRatio"] = f"{result['cost_ratio_all']:.2f}"
            macros[prefix + "SolvedPerDollar"] = f"{result['solved_per_dollar']:.2f}"
            macros[prefix + "P"] = p_tex(result["p_vs_control"])
            if arm != "baseline":
                horizon_contrasts.append([LABEL[arm], f"{delta:+.1f}", p_tex(result["p_vs_control"])])
            summary_rows.append([name.lower(), arm] + [result[key] for key in summary_keys])
            horizon_plot.append([order, arm, result["rate"], result["cost_per_success"],
                                 result["cache_hit_pct"], result["cost_ratio_all"]])
    add("horizon", QUALITY_HEADERS, horizon)
    add("horizon-resources", RESOURCE_HEADERS, horizon_resources)
    add("horizon-contrasts", ["Approach", r"$\Delta$ (pp)", "$p$"], horizon_contrasts)
    output["paper/generated/model-metric-summary.csv"] = csv_text(["cohort", "arm"] + list(summary_keys), summary_rows)
    output["paper/generated/horizon-metrics.csv"] = csv_text(
        ["cohort_order", "arm", "solved_pct", "cost_per_success_usd", "cache_hit_pct", "all_cost_ratio"], horizon_plot)
    macros["HorizonShortUpper"] = str(HORIZON_BOUNDS[0])
    macros["HorizonMediumUpper"] = str(HORIZON_BOUNDS[1])

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
