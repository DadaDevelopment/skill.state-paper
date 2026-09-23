"""Run slop against the extracted manuscript text and apply approved waivers.

npx slop already ran (via `make prose`) and wrote its JSON report. This
script reads that report, drops findings that have an approved waiver in
research/waivers.yml, and fails the build on anything left. A waiver with
approved_by: PENDING_HUMAN_REVIEW does NOT suppress its finding - this
script cannot approve its own waivers, only a human editing waivers.yml can
change that field. See the plan's own rule: an agent is not allowed to grant
itself a waiver.
"""

import json
import os
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANUSCRIPT = os.path.join(REPO, "build", "research", "manuscript-prose.txt")
WAIVERS_PATH = os.path.join(REPO, "research", "waivers.yml")


def load_waivers():
    if not os.path.isfile(WAIVERS_PATH):
        return []
    with open(WAIVERS_PATH) as fh:
        data = yaml.safe_load(fh) or []
    return [w for w in data if w.get("approved_by") not in (None, "PENDING_HUMAN_REVIEW")]


def run_slop():
    if not os.path.isfile(MANUSCRIPT) or not open(MANUSCRIPT, encoding="utf-8").read().strip():
        raise ValueError("missing or empty prose extraction")
    result = subprocess.run(
        ["npx", "slop", "check", MANUSCRIPT, "--format", "json"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    try:
        report = json.loads(result.stdout)
        if not isinstance(report, dict) or not report.get("files"):
            raise ValueError("slop returned no checked files")
        return report
    except (json.JSONDecodeError, ValueError):
        print("slop_gate: could not parse slop output", file=sys.stderr)
        print(result.stdout[-2000:], file=sys.stderr)
        sys.exit(1)


def main():
    approved = load_waivers()
    approved_rule_names = {w["rule"] for w in approved}

    report = run_slop()
    total_unwaived = 0
    for f in report.get("files", []):
        for finding in f.get("findings", []):
            if finding["rule"] in approved_rule_names:
                continue
            total_unwaived += 1
            print(f"UNWAIVED: {finding['rule']} at line {finding.get('line')}")

    if total_unwaived:
        print(f"\nslop_gate: {total_unwaived} unwaived finding(s).")
        return 1
    print("slop_gate: clean (all findings either absent or explicitly approved).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
