"""Fail the build if a relevant, high-priority paper from the literature
watch has not been triaged in research/literature-decisions.yml.

Relevance is a keyword filter over title+abstract, not a full read: arXiv
category filters already point the search at cs.AI/cs.CL/cs.SE, but general
queries like "long horizon" still return unrelated physics/graphics papers
by coincidence of vocabulary. A paper only requires a decision entry if it
matches this filter; everything else is out of scope for this literature
watch and does not need one.
"""

import argparse
import os
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES_PATH = os.path.join(REPO, "research", "literature-candidates.md")
DECISIONS_PATH = os.path.join(REPO, "research", "literature-decisions.yml")

RELEVANCE_PATTERN = re.compile(
    r"(?i)\b(coding agent|llm agent|language model agent|agent memory|"
    r"agent state|agent context|context window|context management|"
    r"context compression|structured state|persistent state|"
    r"long[- ]horizon.*agent|software[- ]engineering agent|swe-bench|"
    r"terminal-?bench|prompt compression)\b"
)

ENTRY_PATTERN = re.compile(
    r"^## \d+\. (?P<title>.+)\n\n"
    r"\*\*Authors\*\*: (?P<authors>.*)  \n"
    r"\*\*Year\*\*: (?P<year>\d+).*\n"
    r"\*\*Citations\*\*: \d+  \n"
    r"\[arXiv:(?P<arxiv_id>[\d.]+)\]",
    re.MULTILINE,
)


def load_candidates():
    with open(CANDIDATES_PATH) as fh:
        text = fh.read()
    entries = []
    blocks = text.split("\n---\n")
    for block in blocks:
        m = ENTRY_PATTERN.search(block)
        if not m:
            continue
        abstract_start = block.find("> ")
        abstract = block[abstract_start:abstract_start + 600] if abstract_start != -1 else ""
        entries.append({
            "title": m.group("title"),
            "arxiv_id": m.group("arxiv_id"),
            "abstract": abstract,
        })
    return entries


def load_decisions():
    if not os.path.isfile(DECISIONS_PATH):
        return {}
    with open(DECISIONS_PATH) as fh:
        data = yaml.safe_load(fh) or []
    return {d["id"]: d for d in data}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(CANDIDATES_PATH):
        print("literature_gate: no candidates file - run the search scripts first", file=sys.stderr)
        return 0 if args.report_only else 1

    candidates = load_candidates()
    decisions = load_decisions()

    relevant = [c for c in candidates if RELEVANCE_PATTERN.search(c["title"] + " " + c["abstract"])]
    print(f"literature_gate: {len(candidates)} candidates, {len(relevant)} pass the relevance filter")

    untriaged = []
    pending = []
    for c in relevant:
        key = f"arxiv:{c['arxiv_id']}"
        d = decisions.get(key)
        if d is None:
            untriaged.append(c)
        elif "PENDING_HUMAN_ACTION" in (d.get("reason") or ""):
            pending.append(c)

    for c in untriaged:
        print(f"UNTRIAGED: {c['title']} (arxiv:{c['arxiv_id']})")
    for c in pending:
        print(f"PENDING (cite decided, not yet applied): {c['title']} (arxiv:{c['arxiv_id']})")

    total_blocking = len(untriaged) + len(pending)
    if total_blocking:
        print(f"\nliterature_gate: {total_blocking} relevant paper(s) not fully resolved.")
        if args.report_only:
            print("report-only mode: not failing the build.")
            return 0
        return 1

    print("literature_gate: clean - every relevant candidate is triaged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
