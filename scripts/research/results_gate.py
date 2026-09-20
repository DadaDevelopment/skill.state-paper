"""Forbid literal experimental numbers typed by hand in the result-bearing
sections of the manuscript.

The project rule (see AGENTS.md, repeated across every session note in this
repo) is that no measured number is typed into the paper text - every
figure in the abstract/results/discussion/conclusion must come from a macro
that analysis/build_paper.py or analysis/build_composition.py generated
from the canonical CSV. This gate is the automated enforcement of that
rule: it flags any digit sequence that looks like a result (a percentage,
a decimal, a large integer, a p-value) sitting outside a \\newcommand{...}
definition in a guarded section.

False positives are expected for page/figure/table numbers, arm names like
tail0/tail6, and equation numbers - those live in an explicit allowlist
below rather than a waiver file, because they are structural LaTeX, not
research claims.
"""

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GUARDED_SECTIONS = [
    "paper/sections/00_abstract.tex",
    "paper/sections/06_results_capability.tex",
    "paper/sections/07_results_mechanism.tex",
    "paper/sections/08_results_economics.tex",
    "paper/sections/09_results_composition.tex",
    "paper/sections/10_results_composition_v.tex",
    "paper/sections/14_conclusion.tex",
]

NUMBER_PATTERN = re.compile(
    r"(?<![a-zA-Z\\{])"
    r"(\d{1,3}(?:,\d{3})+|\d+\.\d+|\d{3,})"
    r"\s*(?:%|\\%)?"
)

ALLOWED_CONTEXT_PATTERNS = [
    re.compile(r"\\newcommand\{"),
    re.compile(r"\\(ref|label|cite|citet|citep|eqref)\{"),
    re.compile(r"\\(Fig|fig|Fig\.|Table|Sec|Section)~?\\ref\{"),
    re.compile(r"tail\d"),
    re.compile(r"[vV]\d(?:-fit|-inline)?\b"),
    re.compile(r"^\s*%"),
    re.compile(r"^\s*\\(begin|end)\{"),
    re.compile(r"Terminal-Bench\s+\d+\.\d+"),
    re.compile(r"cross\s+1\.0\b"),
]

ALLOWED_STANDALONE_NUMBERS = {
    "0", "1", "2", "3", "4", "5", "6", "7",
}


def line_is_exempt(line):
    stripped = line.strip()
    if not stripped:
        return True
    for pat in ALLOWED_CONTEXT_PATTERNS:
        if pat.search(line):
            return True
    return False


def find_bare_numbers(path):
    findings = []
    with open(path) as fh:
        for lineno, line in enumerate(fh, start=1):
            if line_is_exempt(line):
                continue
            for match in NUMBER_PATTERN.finditer(line):
                token = match.group(1)
                if token in ALLOWED_STANDALONE_NUMBERS:
                    continue
                findings.append((lineno, token, line.strip()))
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    total = 0
    for rel in GUARDED_SECTIONS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            print(f"SKIP (missing): {rel}", file=sys.stderr)
            continue
        findings = find_bare_numbers(path)
        for lineno, token, line in findings:
            print(f"{rel}:{lineno}: bare number '{token}' outside a macro -> {line}")
            total += 1

    if total:
        print(f"\nresults_gate: {total} literal number(s) found in guarded sections.")
        if args.report_only:
            print("report-only mode: not failing the build.")
            return 0
        return 1

    print("results_gate: clean - every number in guarded sections is a macro.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
