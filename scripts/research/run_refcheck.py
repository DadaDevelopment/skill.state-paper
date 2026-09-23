"""Run the real CLI, with live retraction and local citation checks.

The installed academic-refchecker CLI does not implement the old web-UI
flags. Exact-identifier OpenAlex requests provide live retraction metadata;
missing metadata remains an audit failure, not a clean result.
"""
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pybtex.database import parse_file

from manuscript_contract import active_graphs, strip_comments

REPO = Path(__file__).resolve().parents[2]
BIB = REPO / "paper/references.bib"
OUTPUT = REPO / "build/research"


def normalize_title(title):
    return re.sub(r"[^\w]+", "", title.casefold())


def citation_findings(root, keys):
    findings = []
    for language, paths in active_graphs(root).items():
        for path in paths:
            text = strip_comments(path.read_text(encoding="utf-8"))
            for match in re.finditer(r"\\cite(?:[A-Za-z]*\*?)?(?:\[[^\]]*\])*\{([^{}]+)\}", text):
                for key in match.group(1).split(","):
                    if key.strip() not in keys:
                        findings.append(f"{language} {path.name}: undefined citation {key.strip()}")
    return findings


def arxiv_withdrawal_status(result, entry, provider_error):
    """Primary-source fallback, explicitly narrower than a retraction registry."""
    match = re.fullmatch(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", result["doi"], re.I)
    if not match:
        return {**result, "error": provider_error}
    url = "https://arxiv.org/abs/" + match.group(1)
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("meta", attrs={"name": "citation_title"})
        identifier = soup.find("meta", attrs={"name": "citation_arxiv_id"})
        authors = [item.get("content", "") for item in soup.find_all("meta", attrs={"name": "citation_author"})]
        cited = [str(person) for person in entry.persons.get("author", [])]
        if not title or normalize_title(title.get("content", "")) != normalize_title(result["title"]):
            raise ValueError("primary-source title does not match")
        if not identifier or identifier.get("content") != match.group(1):
            raise ValueError("primary-source identifier does not match")
        if [normalize_title(author) for author in authors] != [normalize_title(author) for author in cited]:
            raise ValueError("primary-source author list does not match")
        notices = [node.get_text(" ", strip=True) for node in soup.select(".abstract, .comments, .submission-history, .withdrawn, .title")]
        if not soup.select_one(".abstract") or not soup.select_one(".submission-history"):
            raise ValueError("primary-source page is incomplete")
        if re.search(r"\b(?:withdrawn|retracted|retraction)\b", " ".join(notices), re.I):
            raise ValueError("primary-source withdrawal/retraction notice requires review")
        return {**result, "source": "arxiv", "status": "no withdrawal notice", "url": url,
                "matched_title": title["content"], "matched_authors": authors,
                "scope": "Official arXiv abstract, comments, and version history; not a universal retraction claim",
                "provider_error": provider_error, "checked_at": datetime.now(timezone.utc).isoformat()}
    except (requests.RequestException, ValueError, KeyError) as error:
        return {**result, "error": f"{provider_error}; arXiv fallback: {error}"}


def retraction_status(item):
    key, entry = item
    doi = entry.fields.get("doi", "").removeprefix("https://doi.org/")
    if not doi:
        fields = " ".join(entry.fields.values())
        arxiv = re.search(r"(?:arxiv[:\s]+|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})", fields, re.I)
        if arxiv:
            doi = "10.48550/arXiv." + arxiv.group(1)
    result = {"key": key, "title": entry.fields.get("title", ""), "doi": doi}
    if not doi:
        return {**result, "error": "No verified DOI/arXiv identifier available for status lookup"}
    endpoint = "https://api.openalex.org/works/https://doi.org/" + doi
    try:
        response = requests.get(endpoint, params={"select": "id,title,is_retracted,doi"}, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data.get("is_retracted"), bool):
            raise ValueError("missing boolean retraction status")
        if SequenceMatcher(None, normalize_title(result["title"]), normalize_title(data.get("title", ""))).ratio() < .97:
            raise ValueError("identifier resolved to a different title")
        returned_doi = str(data.get("doi", "")).removeprefix("https://doi.org/")
        if returned_doi.casefold() != doi.casefold():
            raise ValueError("identifier mismatch in status response")
        return {**result, "openalex_id": data["id"], "is_retracted": data["is_retracted"],
                "checked_at": datetime.now(timezone.utc).isoformat()}
    except (requests.RequestException, ValueError, KeyError) as error:
        return arxiv_withdrawal_status(result, entry, str(error))


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bibliography = parse_file(str(BIB)).entries
    if not bibliography:
        print("references: empty bibliography", file=sys.stderr)
        return 1
    metadata = {"bib_sha256": hashlib.sha256(BIB.read_bytes()).hexdigest(),
                "expected_references": len(bibliography),
                "citation_errors": citation_findings(REPO, set(bibliography))}
    command = ["academic-refchecker", "--paper", str(BIB), "--report-file",
               str(OUTPUT / "refcheck-bib.json"), "--report-format", "json", "--max-workers", "4"]
    with (OUTPUT / "refcheck-bib.log").open("w") as stdout, (OUTPUT / "refcheck-bib.err").open("w") as stderr:
        try:
            result = subprocess.run(command, cwd=REPO, stdout=stdout, stderr=stderr, timeout=240, check=False)
            metadata["checker_exit_code"] = result.returncode
        except subprocess.TimeoutExpired:
            metadata["checker_exit_code"] = 124
            metadata["error"] = "Reference metadata checker exceeded 240 seconds"
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        metadata["retractions"] = list(executor.map(retraction_status, bibliography.items()))
    (OUTPUT / "refcheck-integrity.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"references: metadata and status checks completed for {len(bibliography)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
