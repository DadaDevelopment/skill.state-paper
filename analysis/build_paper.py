"""Deterministic analysis for the E1 paper tables.

Reads the canonical release CSV and writes LaTeX tables plus a macro file of
inline numbers. No number in the manuscript is typed by hand: every figure in
the text comes from a macro defined here.

Pure stdlib on purpose - the stand and this VM have neither scipy nor pandas,
and a statistics dependency that cannot be installed on the measurement host is
a reproducibility hole.

Usage:
    python3 analysis/build_paper.py [--check]

--check additionally verifies the recomputed headline numbers against the
values published in data/e1-release/README.md and exits non-zero on any
mismatch.
"""

import argparse
import csv
import math
import os
import random
import statistics
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(REPO, "data", "e1-release", "canonical-e1-full.csv")
OUT_TABLES = os.path.join(REPO, "paper", "tables")
OUT_GENERATED = os.path.join(REPO, "paper", "generated")

CONTROL = "baseline"
ARMS = ["tail0", "tail2", "tail6"]
ARM_LABEL = {
    "baseline": "Control (full transcript)",
    "tail0": "State-only ($k{=}0$)",
    "tail2": "State $+2$",
    "tail6": "State $+6$",
}


def log_binom_pmf(k, n, p=0.5):
    """Log of the binomial pmf, used to keep exact tests stable at n>200."""
    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + k * math.log(p)
        + (n - k) * math.log1p(-p)
    )


def binom_tail(k, n, upper):
    """P(X >= k) if upper else P(X <= k), for X ~ Binom(n, 0.5)."""
    rng = range(k, n + 1) if upper else range(0, k + 1)
    return sum(math.exp(log_binom_pmf(i, n, 0.5)) for i in rng)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar test on discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * binom_tail(k, n, upper=False))


def sign_test_exact(gt, lt):
    """Two-sided exact sign test; ties are dropped by the caller."""
    return mcnemar_exact(gt, lt)


def wilson_ci(successes, total, z=1.96):
    """Wilson score interval, valid near 0 and 1 where the normal one is not."""
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    d = 1 + z * z / total
    centre = p + z * z / (2 * total)
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    return ((centre - half) / d, (centre + half) / d)


def spearman(xs, ys):
    """Spearman rho with average ranks for ties; returns (rho, n)."""
    n = len(xs)
    if n < 3:
        return (float("nan"), n)

    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for t in range(i, j + 1):
                r[order[t]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return (num / den if den else float("nan"), n)


def permutation_p(xs, ys, rho_obs, iterations=20000, seed=20260919):
    """Permutation p-value for Spearman rho under a fixed seed."""
    rnd = random.Random(seed)
    ys_shuf = list(ys)
    hits = 0
    target = abs(rho_obs)
    for _ in range(iterations):
        rnd.shuffle(ys_shuf)
        r, _ = spearman(xs, ys_shuf)
        if abs(r) >= target - 1e-12:
            hits += 1
    return (hits + 1) / (iterations + 1)


def load_runs():
    """Read the canonical CSV and coerce the numeric columns."""
    with open(CSV_PATH, newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["trial"] = int(r["trial"])
        r["solved"] = int(r["solved"])
        for k in ("turns", "llm_calls", "tool_calls", "input_tokens",
                  "cache_read_tokens", "output_tokens", "prompt_peak_tokens"):
            r[k] = int(float(r[k])) if r[k] else 0
        r["cost_usd"] = float(r["cost_usd"]) if r["cost_usd"] else 0.0
        r["cache_hit_pct"] = float(r["cache_hit_pct"]) if r["cache_hit_pct"] else 0.0
    return rows


def index_by_cell(rows):
    """Map (task, trial) to the per-condition rows, the unit every test pairs on."""
    cells = defaultdict(dict)
    for r in rows:
        cells[(r["task_id"], r["trial"])][r["condition"]] = r
    return cells


def fmt_p(p):
    """Format a p-value for LaTeX, switching to scientific notation below 0.01."""
    if p >= 0.01:
        return f"{p:.2f}"
    mant, exp = f"{p:.1e}".split("e")
    return f"${mant}\\times 10^{{{int(exp)}}}$"


def tex_escape(s):
    """Escape the one character that actually appears in our identifiers."""
    return s.replace("_", "\\_")


DIGIT_WORDS = {
    "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
    "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine",
}


def macro_name(key):
    """LaTeX control sequences admit letters only, so digits become words.

    Without this a key like CostRatioTail0 expands to the command
    \\CostRatioTail followed by a literal 0, which fails before
    \\begin{document} with a misleading error.
    """
    return "".join(DIGIT_WORDS.get(ch, ch) or ch for ch in key)


def tabular(colspec, header, body):
    """Wrap generated rows into a complete tabular.

    The wrapper lives here rather than in the section files because
    \\input of bare rows INSIDE a tabular breaks TeX's alignment scanner
    ("Misplaced \\noalign" at the following \\bottomrule). Emitting the whole
    environment keeps every generated table self-contained and lets a section
    file input it without knowing its shape.
    """
    return (
        f"\\begin{{tabular}}{{{colspec}}}\n"
        "\\toprule\n"
        f"{header} \\\\\n"
        "\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n"
        "\\end{tabular}"
    )


def table_solve_rate(rows, macros):
    """Solve rate per condition with Wilson intervals."""
    lines = []
    for cond in [CONTROL] + ARMS:
        runs = [r for r in rows if r["condition"] == cond]
        s = sum(r["solved"] for r in runs)
        lo, hi = wilson_ci(s, len(runs))
        lines.append(
            f"{ARM_LABEL[cond]} & {s} / {len(runs)} & {s/len(runs):.3f} & "
            f"[{lo:.3f}, {hi:.3f}] \\\\"
        )
        key = cond.replace("tail", "Tail").replace("baseline", "Base")
        macros[f"Solve{key}"] = f"{s/len(runs):.3f}"
        macros[f"SolveN{key}"] = str(s)
        macros[f"SolveCI{key}"] = f"[{lo:.3f}, {hi:.3f}]"
    return "\n".join(lines)


def table_mcnemar(cells, macros):
    """Paired capability comparison against the same-trial control."""
    lines = []
    for arm in ARMS:
        b = c = both = neither = 0
        for d in cells.values():
            ctl, tre = d.get(CONTROL), d.get(arm)
            if not ctl or not tre:
                continue
            if ctl["solved"] and not tre["solved"]:
                b += 1
            elif tre["solved"] and not ctl["solved"]:
                c += 1
            elif ctl["solved"] and tre["solved"]:
                both += 1
            else:
                neither += 1
        p = mcnemar_exact(b, c)
        n = b + c + both + neither
        lines.append(f"{ARM_LABEL[arm]} & {n} & {b} & {c} & {both} & {fmt_p(p)} \\\\")
        key = arm.replace("tail", "Tail")
        macros[f"McnCtl{key}"] = str(b)
        macros[f"McnArm{key}"] = str(c)
        macros[f"McnBoth{key}"] = str(both)
        macros[f"McnPairs{key}"] = str(n)
        macros[f"McnP{key}"] = fmt_p(p)
    return "\n".join(lines)


def table_cost(cells, macros):
    """Resource ratios on pairs where both arms solved the task."""
    lines = []
    for arm in ARMS:
        ratios = defaultdict(list)
        for d in cells.values():
            ctl, tre = d.get(CONTROL), d.get(arm)
            if not ctl or not tre or not (ctl["solved"] and tre["solved"]):
                continue
            for field, name in (
                ("cost_usd", "cost"),
                ("prompt_peak_tokens", "peak"),
                ("output_tokens", "output"),
                ("cache_read_tokens", "cached"),
                ("turns", "turns"),
            ):
                if ctl[field]:
                    ratios[name].append(tre[field] / ctl[field])
        n = len(ratios["cost"])
        med = {k: statistics.median(v) for k, v in ratios.items()}
        gt = sum(1 for v in ratios["cost"] if v > 1)
        lt = sum(1 for v in ratios["cost"] if v < 1)
        p = sign_test_exact(gt, lt)
        lines.append(
            f"{ARM_LABEL[arm]} & {n} & {med['cost']:.2f}$\\times$ & "
            f"{med['peak']:.2f}$\\times$ & {med['output']:.2f}$\\times$ & "
            f"{med['cached']:.2f}$\\times$ & {fmt_p(p)} \\\\"
        )
        key = arm.replace("tail", "Tail")
        macros[f"CostPairs{key}"] = str(n)
        macros[f"CostRatio{key}"] = f"{med['cost']:.2f}"
        macros[f"PeakRatio{key}"] = f"{med['peak']:.2f}"
        macros[f"OutRatio{key}"] = f"{med['output']:.2f}"
        macros[f"CacheRatio{key}"] = f"{med['cached']:.2f}"
        macros[f"TurnRatio{key}"] = f"{med['turns']:.2f}"
        macros[f"CostSignP{key}"] = fmt_p(p)
    return "\n".join(lines)


def control_median_turns(cells, tasks, trials):
    """Per-task horizon, taken from the control arm so it cannot be circular."""
    out = {}
    for t in tasks:
        vals = [cells[(t, tr)][CONTROL]["turns"] for tr in trials
                if (t, tr) in cells and CONTROL in cells[(t, tr)]]
        if vals:
            out[t] = statistics.median(vals)
    return out


def table_horizon(cells, ctl_turns, macros):
    """Capability loss split at the control's median horizon."""
    cut = statistics.median(ctl_turns.values())
    short = {t for t, v in ctl_turns.items() if v <= cut}
    long_ = {t for t, v in ctl_turns.items() if v > cut}
    macros["HorizonCut"] = f"{cut:.0f}"
    macros["HorizonShort"] = str(len(short))
    macros["HorizonLong"] = str(len(long_))

    lines = []
    for arm in ARMS:
        for label, group in (("short", short), ("long", long_)):
            b = c = 0
            for (task, _trial), d in cells.items():
                if task not in group:
                    continue
                ctl, tre = d.get(CONTROL), d.get(arm)
                if not ctl or not tre:
                    continue
                if ctl["solved"] and not tre["solved"]:
                    b += 1
                elif tre["solved"] and not ctl["solved"]:
                    c += 1
            p = mcnemar_exact(b, c)
            lines.append(f"{ARM_LABEL[arm]} & {label} & {b} & {c} & {fmt_p(p)} \\\\")
            key = arm.replace("tail", "Tail") + label.capitalize()
            macros[f"Hor{key}Ctl"] = str(b)
            macros[f"Hor{key}Arm"] = str(c)
            macros[f"Hor{key}P"] = fmt_p(p)
    return "\n".join(lines)


def table_totals(rows, macros):
    """Series totals, reported with the warning that failures stop early."""
    lines = []
    for cond in [CONTROL] + ARMS:
        runs = [r for r in rows if r["condition"] == cond]
        tot = {k: sum(r[k] for r in runs) for k in
               ("turns", "input_tokens", "cache_read_tokens", "output_tokens")}
        cost = sum(r["cost_usd"] for r in runs)
        lines.append(
            f"{ARM_LABEL[cond]} & \\${cost:,.2f} & {tot['turns']:,} & "
            f"{tot['input_tokens']/1e6:.1f}M & {tot['cache_read_tokens']/1e6:.1f}M & "
            f"{tot['output_tokens']/1e6:.1f}M \\\\"
        )
        key = cond.replace("tail", "Tail").replace("baseline", "Base")
        macros[f"TotCache{key}"] = f"{tot['cache_read_tokens']/1e6:.1f}"
        macros[f"TotCost{key}"] = f"{cost:.2f}"
        macros[f"TotTurns{key}"] = f"{tot['turns']:,}"
    return "\n".join(lines)


def table_efficiency(rows, macros):
    """Solved tasks per million tokens and per dollar - the Pareto view."""
    lines = []
    for cond in [CONTROL] + ARMS:
        runs = [r for r in rows if r["condition"] == cond]
        solved = sum(r["solved"] for r in runs)
        toks = sum(r["input_tokens"] + r["cache_read_tokens"] + r["output_tokens"]
                   for r in runs)
        cost = sum(r["cost_usd"] for r in runs)
        eff_tok = solved / (toks / 1e6) if toks else 0
        eff_cost = solved / cost if cost else 0
        lines.append(
            f"{ARM_LABEL[cond]} & {solved} & {toks/1e6:.1f}M & \\${cost:,.2f} & "
            f"{eff_tok:.2f} & {eff_cost:.1f} \\\\"
        )
        key = cond.replace("tail", "Tail").replace("baseline", "Base")
        macros[f"EffTok{key}"] = f"{eff_tok:.2f}"
        macros[f"EffCost{key}"] = f"{eff_cost:.1f}"
    return "\n".join(lines)


def table_stop_reasons(rows, macros):
    """How runs ended, so a budget stop is never read as a capability failure."""
    sr = defaultdict(lambda: defaultdict(int))
    for r in rows:
        sr[r["condition"]][r["stop_reason"]] += 1
    reasons = sorted({k for d in sr.values() for k in d})
    lines = []
    for cond in [CONTROL] + ARMS:
        cnt = " & ".join(str(sr[cond].get(x, 0)) for x in reasons)
        lines.append(f"{ARM_LABEL[cond]} & {cnt} \\\\")
    macros["StopReasonList"] = ", ".join(tex_escape(x) for x in reasons)
    macros["StopReasonCols"] = str(len(reasons))
    header = " & ".join(tex_escape(x) for x in reasons)
    return "\n".join(lines), header


def horizon_cost_trend(cells, ctl_turns, tasks, trials, macros):
    """Pre-registered RQ2 test: does the cost ratio fall as horizon grows?"""
    xs, ys = [], []
    for t in tasks:
        rs = []
        for tr in trials:
            d = cells.get((t, tr), {})
            ctl, tre = d.get(CONTROL), d.get("tail0")
            if ctl and tre and ctl["solved"] and tre["solved"] and ctl["cost_usd"]:
                rs.append(tre["cost_usd"] / ctl["cost_usd"])
        if rs and t in ctl_turns:
            xs.append(ctl_turns[t])
            ys.append(statistics.median(rs))
    rho, n_rho = spearman(xs, ys)
    p_rho = permutation_p(xs, ys, rho)
    macros["RhoHorizonCost"] = f"{rho:+.2f}"
    macros["RhoHorizonCostN"] = str(n_rho)
    macros["RhoHorizonCostP"] = fmt_p(p_rho)


def build(rows):
    """Produce every table body and every inline macro from the run rows."""
    cells = index_by_cell(rows)
    tasks = sorted({r["task_id"] for r in rows})
    trials = sorted({r["trial"] for r in rows})
    out, macros = {}, {}

    macros["EOneRuns"] = str(len(rows))
    macros["EOneTasks"] = str(len(tasks))
    macros["EOneTrials"] = str(len(trials))
    macros["EOneConditions"] = str(len({r["condition"] for r in rows}))
    macros["EOneModel"] = tex_escape(sorted({r["model"] for r in rows})[0])
    macros["EOneCorpus"] = sorted({r["corpus"] for r in rows})[0]
    macros["EOneSpend"] = f"{sum(r['cost_usd'] for r in rows):.2f}"
    macros["EOneTurns"] = f"{sum(r['turns'] for r in rows):,}"
    macros["EOnePlugin"] = sorted({r["plugin_revision"] for r in rows})[0]
    macros["EOneSchema"] = sorted({r["schema_revision"] for r in rows})[0]

    out["t1_solve_rate.tex"] = tabular(
        "@{}lrrr@{}", "Condition & Solved / runs & Rate & 95\\% CI",
        table_solve_rate(rows, macros))
    out["t2_mcnemar.tex"] = tabular(
        "@{}lrrrrr@{}",
        "Condition & Pairs & Control only & Arm only & Both & $p$",
        table_mcnemar(cells, macros))
    out["t3_cost.tex"] = tabular(
        "@{}lrrrrrr@{}",
        "Condition & Pairs & Cost & Peak prompt & Output & Cached & $p$",
        table_cost(cells, macros))

    ctl_turns = control_median_turns(cells, tasks, trials)
    out["t4_horizon.tex"] = tabular(
        "@{}llrrr@{}",
        "Condition & Horizon & Control only & Arm only & $p$",
        table_horizon(cells, ctl_turns, macros))
    out["t5_totals.tex"] = tabular(
        "@{}lrrrrr@{}",
        "Condition & Cost & Turns & Input & Cached & Output",
        table_totals(rows, macros))
    out["t6_efficiency.tex"] = tabular(
        "@{}lrrrrr@{}",
        "Condition & Solved & Tokens & Cost & Solved/Mtok & Solved/\\$",
        table_efficiency(rows, macros))

    body, header = table_stop_reasons(rows, macros)
    out["t7_stop_reasons.tex"] = tabular(
        "@{}l" + "r" * len(header.split("&")) + "@{}",
        "Condition & " + header, body)

    horizon_cost_trend(cells, ctl_turns, tasks, trials, macros)
    write_plot_data(rows, cells, ctl_turns, macros,
                    os.path.join(REPO, "paper", "figures", "data"))
    return out, macros


def write_plot_data(rows, cells, ctl_turns, macros, outdir):
    """Emit pgfplots coordinate files so figures carry measured data.

    A figure drawn from numbers retyped by hand is the same reproducibility
    hole as a table retyped by hand, so the plots read the same CSV as
    everything else.
    """
    os.makedirs(outdir, exist_ok=True)

    def w(name, text):
        with open(os.path.join(outdir, name), "w") as fh:
            fh.write(text)

    order = [CONTROL] + ARMS
    short_label = {"baseline": "control", "tail0": "$k{=}0$",
                   "tail2": "$k{=}2$", "tail6": "$k{=}6$"}

    lines = []
    for i, cond in enumerate(order):
        runs = [r for r in rows if r["condition"] == cond]
        s_ = sum(r["solved"] for r in runs)
        rate = s_ / len(runs)
        lo, hi = wilson_ci(s_, len(runs))
        lines.append(f"{i} {rate:.4f} {rate-lo:.4f} {hi-rate:.4f} {short_label[cond]}")
    w("solve_rate.dat", "x rate elo ehi label\n" + "\n".join(lines) + "\n")

    lines = []
    for i, arm in enumerate(ARMS):
        b = c = 0
        for d in cells.values():
            ctl, tre = d.get(CONTROL), d.get(arm)
            if not ctl or not tre:
                continue
            if ctl["solved"] and not tre["solved"]:
                b += 1
            elif tre["solved"] and not ctl["solved"]:
                c += 1
        lines.append(f"{i} {b} {c} {short_label[arm]}")
    w("discordance.dat", "x ctlonly armonly label\n" + "\n".join(lines) + "\n")

    cut = statistics.median(ctl_turns.values())
    groups = {"short": {t for t, v in ctl_turns.items() if v <= cut},
              "long": {t for t, v in ctl_turns.items() if v > cut}}
    lines = []
    for i, arm in enumerate(ARMS):
        row = [str(i)]
        for label in ("short", "long"):
            b = c = 0
            for (task, _tr), d in cells.items():
                if task not in groups[label]:
                    continue
                ctl, tre = d.get(CONTROL), d.get(arm)
                if not ctl or not tre:
                    continue
                if ctl["solved"] and not tre["solved"]:
                    b += 1
                elif tre["solved"] and not ctl["solved"]:
                    c += 1
            row.append(f"{b - c}")
        row.append(short_label[arm])
        lines.append(" ".join(row))
    w("horizon_deficit.dat", "x short long label\n" + "\n".join(lines) + "\n")

    lines = []
    for cond in order:
        runs = [r for r in rows if r["condition"] == cond]
        solved = sum(r["solved"] for r in runs)
        cost = sum(r["cost_usd"] for r in runs)
        peak = statistics.median([r["prompt_peak_tokens"] for r in runs])
        lines.append(f"{cost:.2f} {solved} {peak:.0f} {short_label[cond]}")
    w("pareto.dat", "cost solved peak label\n" + "\n".join(lines) + "\n")

    lines = []
    for i, cond in enumerate(order):
        runs = [r for r in rows if r["condition"] == cond]
        tot = sum(r["input_tokens"] + r["cache_read_tokens"] + r["output_tokens"]
                  for r in runs)
        cached = sum(r["cache_read_tokens"] for r in runs)
        outp = sum(r["output_tokens"] for r in runs)
        unc = sum(r["input_tokens"] for r in runs)
        lines.append(f"{i} {unc/1e6:.2f} {cached/1e6:.2f} {outp/1e6:.2f} "
                     f"{short_label[cond]}")
    w("token_classes.dat", "x uncached cached output label\n" + "\n".join(lines) + "\n")

    lines = []
    for i, cond in enumerate(order):
        pairs = []
        for d in cells.values():
            ctl, tre = d.get(CONTROL), d.get(cond)
            if not ctl or not tre or not (ctl["solved"] and tre["solved"]):
                continue
            if ctl["cost_usd"] and ctl["prompt_peak_tokens"]:
                pairs.append((tre["prompt_peak_tokens"] / ctl["prompt_peak_tokens"],
                              tre["cost_usd"] / ctl["cost_usd"]))
        if pairs:
            mp = statistics.median([a for a, _ in pairs])
            mc = statistics.median([b for _, b in pairs])
            lines.append(f"{mp:.3f} {mc:.3f} {short_label[cond]}")
    w("prompt_vs_cost.dat", "peak cost label\n" + "\n".join(lines) + "\n")

    macros["FigDataNote"] = "generated from the canonical run data"


def check_against_release(macros):
    """Gate the recomputation against the numbers published in the release."""
    expected = {
        "EOneRuns": "1044",
        "SolveBase": "0.613",
        "SolveTail0": "0.349",
        "SolveTail2": "0.452",
        "SolveTail6": "0.590",
        "McnCtlTail0": "82",
        "McnArmTail0": "13",
        "McnBothTail0": "78",
        "CostPairsTail0": "78",
        "CostRatioTail0": "2.57",
        "PeakRatioTail0": "0.47",
        "OutRatioTail0": "4.55",
        "CostRatioTail6": "1.15",
        "HorizonShort": "45",
        "HorizonLong": "42",
        "EOneSpend": "57.39",
    }
    bad = []
    for k, want in expected.items():
        got = macros.get(k)
        if got != want:
            bad.append(f"  {k}: recomputed {got!r} != published {want!r}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows = load_runs()
    tables, macros = build(rows)

    os.makedirs(OUT_TABLES, exist_ok=True)
    os.makedirs(OUT_GENERATED, exist_ok=True)
    for name, body in tables.items():
        with open(os.path.join(OUT_TABLES, name), "w") as fh:
            fh.write(body + "%\n")

    with open(os.path.join(OUT_GENERATED, "numbers.tex"), "w") as fh:
        fh.write("% GENERATED by analysis/build_paper.py - do not edit.\n")
        for k in sorted(macros):
            fh.write(f"\\newcommand{{\\{macro_name(k)}}}{{{macros[k]}}}\n")

    print(f"wrote {len(tables)} tables to paper/tables/")
    print(f"wrote {len(macros)} macros to paper/generated/numbers.tex")

    if args.check:
        bad = check_against_release(macros)
        if bad:
            print("\nINTEGRITY FAILURE: recomputed != published release")
            print("\n".join(bad))
            return 1
        print("integrity check: recomputed headline numbers match the release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
