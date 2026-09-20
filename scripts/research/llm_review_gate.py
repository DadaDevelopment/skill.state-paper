"""Enforce the BLOCKER/MAJOR -> FAIL, MINOR -> report-only policy against
an independent reviewer's JSON verdict.

Takes the reviewer's output file as its one argument. Does not call any
LLM itself - see llm_review.py for why the review must be dispatched as an
isolated subagent instead of from inside this script.
"""

import json
import sys


def main():
    if len(sys.argv) != 2:
        print("usage: llm_review_gate.py <reviewer-output.json>", file=sys.stderr)
        return 2

    with open(sys.argv[1]) as fh:
        review = json.load(fh)

    issues = review.get("issues", [])
    blockers = [i for i in issues if i.get("severity") == "blocker"]
    majors = [i for i in issues if i.get("severity") == "major"]
    minors = [i for i in issues if i.get("severity") == "minor"]

    for i in minors:
        print(f"MINOR [{i.get('category')}] {i.get('location')}: {i.get('reason')}")

    for i in majors:
        print(f"MAJOR [{i.get('category')}] {i.get('location')}: {i.get('reason')}")

    for i in blockers:
        print(f"BLOCKER [{i.get('category')}] {i.get('location')}: {i.get('reason')}")

    print(f"\nllm_review_gate: {len(blockers)} blocker(s), {len(majors)} major(s), "
          f"{len(minors)} minor(s) (report only)")

    if blockers or majors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
