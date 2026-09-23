import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/research"))
from refcheck_gate import validate_report


def valid():
    report = {"summary": {"total_references_processed": 1, "total_errors_found": 0,
                          "total_unverified_refs": 0, "flagged_records": 0}, "records": []}
    integrity = {"expected_references": 1, "bib_sha256": "hash", "checker_exit_code": 0,
                 "citation_errors": [], "retractions": [{"key": "paper", "is_retracted": False}]}
    return report, integrity


def test_verified_report_passes():
    report, integrity = valid()
    assert validate_report(report, integrity, "hash") == []


@pytest.mark.parametrize("report", [{}, [], {"summary": {}}, {"summary": {"total_references_processed": 0}}])
def test_empty_or_malformed_report_fails_closed(report):
    assert validate_report(report, valid()[1], "hash")


@pytest.mark.parametrize("field", ["total_errors_found", "total_unverified_refs", "flagged_records"])
def test_each_error_class_fails(field):
    report, integrity = valid()
    report["summary"][field] = 1
    assert validate_report(report, integrity, "hash")


def test_stale_or_incomplete_coverage_fails():
    report, integrity = valid()
    assert validate_report(report, integrity, "changed")
    integrity["expected_references"] = 2
    assert validate_report(report, integrity, "hash")


def test_warnings_are_not_errors_but_nested_errors_fail():
    report, integrity = valid()
    report["records"] = [{"error_type": "multiple", "_original_errors": [{"warning_type": "year"}, {"info_type": "url"}]}]
    assert validate_report(report, integrity, "hash") == []
    report["records"][0]["_original_errors"].append({"error_type": "author"})
    assert validate_report(report, integrity, "hash")


@pytest.mark.parametrize("status", [None, True, "false"])
def test_retracted_or_unknown_status_fails(status):
    report, integrity = valid()
    integrity["retractions"][0]["is_retracted"] = status
    assert validate_report(report, integrity, "hash")


def test_undefined_citation_or_checker_crash_fails():
    report, integrity = valid()
    integrity["citation_errors"].append("undefined citation")
    assert validate_report(report, integrity, "hash")
    integrity = valid()[1]
    integrity["checker_exit_code"] = 124
    assert validate_report(report, integrity, "hash")


def test_primary_source_fallback_requires_title_author_and_url_evidence():
    report, integrity = valid()
    integrity["retractions"] = [{"key": "paper", "source": "arxiv", "status": "no withdrawal notice"}]
    assert validate_report(report, integrity, "hash")
    integrity["retractions"][0].update(matched_title="Title", matched_authors=["Author"],
                                        url="https://arxiv.org/abs/2210.03629")
    assert validate_report(report, integrity, "hash") == []
