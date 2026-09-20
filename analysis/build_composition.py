"""Generate the composition (V-axis) tables, figure data and macros.

Same contract as build_paper.py: every number the manuscript prints about the
composition axis is computed here from the run log and written as a macro or a
table. Nothing is typed into the LaTeX source by hand.

The V-axis moves exactly one factor: how much of the state the RUNTIME writes
without asking the model. Tail is frozen at 0 and the schema at L2 in every
cell, so a gap between neighbouring rungs names a single delegated component.

Deliberately NOT read from the log: verified_observations, verified_modifications,
verified_commands, stale_turns, coverage_gap_turns. Those columns are identically
zero across all 488 instrumented rows and coverage_complete is uniformly True,
so they are dead instrumentation rather than measurements. Using them would
repeat this project's defect #12. Every claim here rests on the task verifier's
verdict and on token counts, which are authoritative.
"""

import json
import math
import os
import statistics
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_TABLES = os.path.join(REPO, "paper", "tables")
OUT_GENERATED = os.path.join(REPO, "paper", "generated")
OUT_FIGDATA = os.path.join(REPO, "paper", "figures", "data")

CONTROL = "control"
LADDER = ["hybrid-v1", "hybrid-v3", "hybrid-v6", "hybrid-v7"]

RUNG_LABEL = {
    "hybrid-v1": ("v1", "files"),
    "hybrid-v3": ("v3", "+ commands"),
    "hybrid-v6": ("v6", "+ tests"),
    "hybrid-v7": ("v7", "+ failures"),
}

DIGIT_WORDS = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
               "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"}


def macro_name(key):
    """LaTeX control sequences cannot contain digits, so spell them out."""
    return "".join(str(DIGIT_WORDS.get(ch, ch)) for ch in key)


def exact_mcnemar(b, c):
    """Two-sided exact McNemar via the binomial, no scipy on this stand."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def fmt_p(p):
    if p >= 0.01:
        return f"{p:.2f}"
    exp = int(math.floor(math.log10(p)))
    mant = p / (10 ** exp)
    return f"${mant:.1f}\\times 10^{{{exp}}}$"


def load(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        REPO, "data", "v-axis", "vaxis-trial1.jsonl")
    rows = load(src)

    cell = {(r["task"], r["arm"]): r for r in rows}
    tasks = sorted({r["task"] for r in rows})
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["arm"], []).append(r)

    macros = {}
    os.makedirs(OUT_TABLES, exist_ok=True)
    os.makedirs(OUT_GENERATED, exist_ok=True)
    os.makedirs(OUT_FIGDATA, exist_ok=True)

    macros["VTasks"] = str(len(tasks))
    macros["VArms"] = str(len(LADDER) + 1)
    macros["VRuns"] = str(sum(len(by_arm.get(a, [])) for a in [CONTROL] + LADDER))
    macros["VTrials"] = "1"

    def rate(arm):
        rs = by_arm[arm]
        return sum(1 for r in rs if r["solved"]) / len(rs)

    def paired(arm_lo, arm_hi):
        b = c = 0
        for t in tasks:
            x, y = cell.get((t, arm_lo)), cell.get((t, arm_hi))
            if not x or not y:
                continue
            if x["solved"] and not y["solved"]:
                b += 1
            elif y["solved"] and not x["solved"]:
                c += 1
        return b, c

    def cost_ratio(arm):
        pr = []
        for t in tasks:
            x, y = cell.get((t, CONTROL)), cell.get((t, arm))
            if x and y and x["solved"] and y["solved"] and x["cost_usd"] > 0:
                pr.append(y["cost_usd"] / x["cost_usd"])
        return statistics.median(pr), len(pr)

    def ratio_on_paired(arm, field):
        pr = []
        for t in tasks:
            x, y = cell.get((t, CONTROL)), cell.get((t, arm))
            if x and y and x["solved"] and y["solved"] and x[field] > 0:
                pr.append(y[field] / x[field])
        return statistics.median(pr)

    ctl_rate = rate(CONTROL)
    macros["VBaseRate"] = f"{ctl_rate:.3f}"
    ctl_cost = sum(r["cost_usd"] for r in by_arm[CONTROL])
    ctl_solved = sum(1 for r in by_arm[CONTROL] if r["solved"])
    macros["VBaseSolved"] = str(ctl_solved)
    macros["VBaseCostPer"] = f"{ctl_solved / ctl_cost:.1f}"

    t1 = ["\\begin{tabular}{@{}llrrrrr@{}}", "\\toprule",
          "Rung & Adds & Solved & Rate & Cost ratio & Turns & Output \\\\",
          "\\midrule",
          f"\\Control{{}} & full transcript & {ctl_solved} & {ctl_rate:.3f} "
          f"& $1.00\\times$ & $1.00\\times$ & $1.00\\times$ \\\\",
          "\\midrule"]
    for arm in LADDER:
        tag, adds = RUNG_LABEL[arm]
        rs = by_arm[arm]
        s = sum(1 for r in rs if r["solved"])
        cr, npairs = cost_ratio(arm)
        tr = ratio_on_paired(arm, "turns")
        ot = ratio_on_paired(arm, "output_tokens")
        key = macro_name(tag.capitalize())
        macros[f"VRate{key}"] = f"{s / len(rs):.3f}"
        macros[f"VSolved{key}"] = str(s)
        macros[f"VCost{key}"] = f"{cr:.2f}"
        macros[f"VTurns{key}"] = f"{tr:.2f}"
        macros[f"VOut{key}"] = f"{ot:.2f}"
        macros[f"VPairs{key}"] = str(npairs)
        macros[f"VCostPer{key}"] = f"{s / sum(r['cost_usd'] for r in rs):.1f}"
        t1.append(f"{tag} & {adds} & {s} & {s / len(rs):.3f} & "
                  f"${cr:.2f}\\times$ & ${tr:.2f}\\times$ & ${ot:.2f}\\times$ \\\\")
    t1 += ["\\bottomrule", "\\end{tabular}"]

    t2 = ["\\begin{tabular}{@{}lrrl@{}}", "\\toprule",
          "Step & Lower solves only & Higher solves only & $p$ \\\\",
          "\\midrule"]
    steps = [("hybrid-v1", "hybrid-v3"), ("hybrid-v3", "hybrid-v6"),
             ("hybrid-v6", "hybrid-v7"), ("hybrid-v1", "hybrid-v7")]
    for lo, hi in steps:
        b, c = paired(lo, hi)
        p = exact_mcnemar(b, c)
        lk = macro_name(RUNG_LABEL[lo][0].capitalize())
        hk = macro_name(RUNG_LABEL[hi][0].capitalize())
        macros[f"VStep{lk}{hk}Lo"] = str(b)
        macros[f"VStep{lk}{hk}Hi"] = str(c)
        macros[f"VStep{lk}{hk}P"] = fmt_p(p)
        t2.append(f"{RUNG_LABEL[lo][0]} $\\rightarrow$ {RUNG_LABEL[hi][0]} "
                  f"& {b} & {c} & {fmt_p(p)} \\\\")
    t2 += ["\\bottomrule", "\\end{tabular}"]

    t3 = ["\\begin{tabular}{@{}lrrl@{}}", "\\toprule",
          "Rung & Control only & Rung only & $p$ \\\\", "\\midrule"]
    for arm in LADDER:
        b, c = paired(CONTROL, arm)
        p = exact_mcnemar(b, c)
        key = macro_name(RUNG_LABEL[arm][0].capitalize())
        macros[f"VCtl{key}Lo"] = str(b)
        macros[f"VCtl{key}Hi"] = str(c)
        macros[f"VCtl{key}P"] = fmt_p(p)
        macros[f"VCtl{key}Net"] = str(c - b)
        t3.append(f"{RUNG_LABEL[arm][0]} & {b} & {c} & {fmt_p(p)} \\\\")
    t3 += ["\\bottomrule", "\\end{tabular}"]

    for name, body in [("v1_ladder.tex", t1), ("v2_steps.tex", t2),
                       ("v3_vs_control.tex", t3)]:
        with open(os.path.join(OUT_TABLES, name), "w") as fh:
            fh.write("\n".join(body) + "%\n")

    lines = []
    for i, arm in enumerate(LADDER):
        rs = by_arm[arm]
        s = sum(1 for r in rs if r["solved"])
        cr, _ = cost_ratio(arm)
        lines.append(f"{i} {s / len(rs):.4f} {cr:.4f} {RUNG_LABEL[arm][0]}")
    with open(os.path.join(OUT_FIGDATA, "ladder.dat"), "w") as fh:
        fh.write("x rate cost label\n" + "\n".join(lines) + "\n")
        fh.write(f"# control rate {ctl_rate:.4f}\n")

    with open(os.path.join(OUT_FIGDATA, "ladder_control.dat"), "w") as fh:
        fh.write("x rate\n")
        fh.write(f"-0.5 {ctl_rate:.4f}\n{len(LADDER) - 0.5} {ctl_rate:.4f}\n")

    path = os.path.join(OUT_GENERATED, "composition.tex")
    with open(path, "w") as fh:
        fh.write("% GENERATED by analysis/build_composition.py - do not edit.\n")
        for k in sorted(macros):
            fh.write(f"\\newcommand{{\\{macro_name(k)}}}{{{macros[k]}}}\n")

    print(f"wrote 3 tables to {os.path.relpath(OUT_TABLES, REPO)}/")
    print(f"wrote {len(macros)} macros to {os.path.relpath(path, REPO)}")
    print(f"ladder: control {ctl_rate:.3f} | " + " ".join(
        f"{RUNG_LABEL[a][0]} {rate(a):.3f}" for a in LADDER))
    print("cost ratio vs control: " + " ".join(
        f"{RUNG_LABEL[a][0]} {cost_ratio(a)[0]:.2f}x" for a in LADDER))


if __name__ == "__main__":
    main()
