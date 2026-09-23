"""Reject hand-written measured numbers in both active manuscript input graphs.

Structural constants in Methods/model sections and generated tables are outside
this gate's scope. A citation, reference, or label masks only its own argument;
it cannot exempt an experimental number elsewhere on the same source line.
"""
import argparse
import re
import sys
from pathlib import Path
from manuscript_contract import GraphError, active_graphs, mask_commands, strip_comments

REPO = Path(__file__).resolve().parents[2]
GUARDED = re.compile(r"abstract|results?|conclusion|threats?|discussion|capability|economics", re.I)
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z\d])(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{3,}|\d+(?=\s*\\?%))(?![A-Za-z\d])")
P_VALUE_PATTERN = re.compile(r"\bp\s*(?:[<=>]|\\leq?|\\geq?)\s*(\d+(?:\.\d+)?)")


def guarded(path):
    return "sections" in path.parts and bool(GUARDED.search(path.stem))


def find_bare_numbers(path):
    source = strip_comments(Path(path).read_text(encoding="utf-8"))
    masked = mask_commands(source, {"cite", "citet", "citep", "citealp", "citealt", "ref", "eqref", "label", "input", "include", "sharedtable", "sharedfigure"})
    findings = []
    for lineno, line in enumerate(masked.splitlines(), 1):
        found = [(m.start(), m.group()) for m in NUMBER_PATTERN.finditer(line)]
        found += [(m.start(1), m.group(1)) for m in P_VALUE_PATTERN.finditer(line)]
        for _, token in sorted(set(found)):
            findings.append((lineno, token, source.splitlines()[lineno - 1].strip()))
    return findings


def check(root=REPO):
    failures = []
    for language, graph in active_graphs(root).items():
        sections = [path for path in graph if guarded(path)]
        if not sections:
            raise GraphError(f"{language}: no active result-bearing sections found")
        for path in sections:
            for line, token, context in find_bare_numbers(path):
                failures.append(f"{path.relative_to(root)}:{line}: literal measured number {token!r}: {context}")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    try:
        failures = check()
    except (GraphError, OSError) as error:
        print(f"results_gate: {error}", file=sys.stderr)
        return 1
    for failure in failures:
        print(failure)
    if failures:
        print(f"results_gate: {len(failures)} literal measured number(s) in active EN/RU sections.")
        return 0 if args.report_only else 1
    print("results_gate: active EN/RU result-bearing sections use generated numbers; all inputs resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
