"""Fail on missing, stale, incomplete, unverified, or erroneous references.

Reads academic-refchecker's actual CLI schema. Informational suggestions and
year/venue warnings remain warnings; all metadata errors are hard failures.
The separate integrity report covers live retraction status and citation keys.
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def validate_report(report, integrity, bibliography_hash):
    failures = []
    if not isinstance(report, dict) or not isinstance(report.get("summary"), dict):
        return ["missing reference summary"]
    if not isinstance(integrity, dict):
        return ["missing integrity summary"]
    summary = report["summary"]
    expected = integrity.get("expected_references")
    if not isinstance(expected, int) or expected <= 0:
        failures.append("empty or malformed reference coverage")
    if integrity.get("bib_sha256") != bibliography_hash:
        failures.append("bibliography changed after verification")
    if integrity.get("checker_exit_code") != 0:
        failures.append(f"reference checker did not finish successfully: {integrity.get('checker_exit_code')}")
    if summary.get("total_references_processed") != expected:
        failures.append("checker did not cover the complete bibliography")
    for field in ("total_errors_found", "total_unverified_refs", "flagged_records"):
        count = summary.get(field)
        if not isinstance(count, int) or count < 0:
            failures.append(f"missing or invalid summary field: {field}")
        elif count:
            failures.append(f"{field}: {count}")
    if not isinstance(report.get("records"), list):
        failures.append("missing checker records")
    else:
        for record in report["records"]:
            # Aggregated records combine info/warnings and errors. Typed
            # children preserve the original checker's severity distinction.
            for entry in record.get("_original_errors", [record]):
                if entry.get("error_type"):
                    failures.append(f"{record.get('ref_title')}: {entry['error_type']}: {entry.get('error_details', '')}")
    if not isinstance(integrity.get("citation_errors"), list):
        failures.append("missing citation-key verification")
    else:
        failures.extend(integrity["citation_errors"])
    retractions = integrity.get("retractions")
    if not isinstance(retractions, list) or len(retractions) != expected:
        failures.append("incomplete live retraction-status coverage")
    else:
        keys = [entry.get("key") for entry in retractions]
        if len(set(keys)) != len(keys) or None in keys:
            failures.append("duplicate or missing retraction-status keys")
        for entry in retractions:
            arxiv_evidence = (entry.get("source") == "arxiv" and entry.get("status") == "no withdrawal notice"
                              and entry.get("matched_title") and entry.get("matched_authors")
                              and str(entry.get("url", "")).startswith("https://arxiv.org/abs/"))
            if entry.get("is_retracted") is not False and not arxiv_evidence:
                failures.append(f"{entry.get('key')}: retraction status not clean: {entry.get('error', entry.get('is_retracted'))}")
    return failures


def main():
    try:
        report = json.loads((REPO / "build/research/refcheck-bib.json").read_text(encoding="utf-8"))
        integrity = json.loads((REPO / "build/research/refcheck-integrity.json").read_text(encoding="utf-8"))
        digest = hashlib.sha256((REPO / "paper/references.bib").read_bytes()).hexdigest()
        failures = validate_report(report, integrity, digest)
    except (OSError, ValueError, TypeError) as error:
        failures = [f"missing or malformed verification output: {error}"]
    for failure in failures:
        print(f"refcheck_gate: {failure}", file=sys.stderr)
    if failures:
        return 1
    summary = report["summary"]
    print(f"refcheck_gate: {summary['total_references_processed']} references verified; "
          f"{summary.get('total_warnings_found', 0)} metadata warnings; "
          "live status and active citation keys checked")
    for entry in integrity["retractions"]:
        if entry.get("source") == "arxiv":
            print(f"refcheck_gate: {entry['key']}: official arXiv page has no withdrawal notice "
                  f"(registry metadata unavailable/inconsistent; narrower status scope)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
