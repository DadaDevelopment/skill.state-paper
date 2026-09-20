"""Turn RefChecker's JSON output into a pass/fail gate.

Reads build/research/refcheck-bib.json (written by run_refcheck.py) and
applies the severity policy from the plan: metadata/DOI/title/author
mismatches, retracted references, likely hallucinations, and unresolved
references are hard failures. Missing-literature suggestions and minor
year/venue mismatches are warnings only.
"""

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REFCHECK_PATH = os.path.join(REPO, "build", "research", "refcheck-bib.json")

FAIL_ERROR_TYPES = {
    "unverified",
    "url",
    "arxiv_id",
    "doi",
    "title",
    "author",
    "retracted",
    "hallucination",
}


def load_result():
    with open(REFCHECK_PATH) as fh:
        raw = fh.read()
    idx = raw.find("\n{\n")
    if idx == -1:
        idx = raw.find("{")
    return json.loads(raw[idx:])


def main():
    if not os.path.isfile(REFCHECK_PATH):
        print(f"refcheck_gate: {REFCHECK_PATH} missing - run run_refcheck.py first", file=sys.stderr)
        return 1

    d = load_result()
    summary = d.get("summary", {})
    print(f"refcheck_gate: {summary.get('total_refs')} refs, "
          f"{summary.get('verified_count')} verified, "
          f"{summary.get('errors_count')} with errors, "
          f"{summary.get('warnings_count')} with warnings")

    failures = []
    for ref in d.get("references", []):
        for err in ref.get("errors", []):
            failures.append((ref["title"], err.get("error_type"), err.get("error_details")))

    retractions = d.get("retractions", {})
    if retractions.get("retracted", 0) > 0:
        for r in retractions.get("results", []):
            if r.get("status") == "retracted":
                failures.append((r.get("title"), "retracted", "flagged retracted by OpenAlex"))

    citation_order = d.get("citation_order", {})
    if citation_order.get("counts", {}).get("undefined", 0) > 0:
        failures.append(("citation order", "undefined", "undefined citation marker(s) present"))

    if failures:
        print(f"\nrefcheck_gate: {len(failures)} FAIL-level finding(s):")
        for title, kind, detail in failures:
            print(f"  [{kind}] {title}: {detail}")
        return 1

    print("refcheck_gate: clean - no FAIL-level reference issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
