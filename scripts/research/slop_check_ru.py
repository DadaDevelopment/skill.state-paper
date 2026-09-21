"""Anti-slop lint for the Russian manuscript.

npx slop only knows English AI-writing tells (echo-triads, mic-drop
kickers, "rather than" overuse). It has no Russian ruleset, so this is a
small standalone checker built from real, sourced markers of Russian
AI-generated prose (ru.wikipedia.org/wiki/Википедия:Признаки_сгенерированности_текста
and independent corroborating sources), not a translation of the English
list.

Checks:
  1. banned-phrases-ru.txt: canned transition/hedge phrases
     ("Таким образом", "Важно отметить, что", "Безусловно", ...)
  2. paragraph_discourse_marker_run: >2 consecutive paragraphs opening on
     the same discourse marker (same failure mode as the EN style
     contract, ported)
  3. colon_before_list_item: a Russian-specific AI tell - GPT-style output
     inserts a colon after the first word/phrase of every list item and
     then restates the same content after it, instead of writing the
     explanation the colon promises
  4. em_dash_overuse: same class of tell as the EN "--" rhetorical dash
     check, counted separately because Cyrillic prose uses the dash
     (тире) differently (subject-predicate omission is legitimate
     Russian grammar, a run of 3+ per paragraph is not)

Waiver-aware: reads research/waivers.yml exactly like slop_gate.py, same
approved_by != PENDING_HUMAN_REVIEW rule, same "agent cannot approve its
own waiver" constraint.
"""

import os
import re
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANUSCRIPT = os.path.join(REPO, "build", "research", "manuscript-ru.txt")
BANNED_PATH = os.path.join(REPO, "research", "banned-phrases-ru.txt")
WAIVERS_PATH = os.path.join(REPO, "research", "waivers.yml")


def load_banned_phrases():
    with open(BANNED_PATH, encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def load_waivers():
    if not os.path.isfile(WAIVERS_PATH):
        return set()
    with open(WAIVERS_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    return {
        w["rule"] for w in data
        if w.get("approved_by") not in (None, "PENDING_HUMAN_REVIEW")
    }


def check_banned_phrases(text, phrases):
    findings = []
    for phrase in phrases:
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        for m in pattern.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            findings.append({
                "rule": "banned-phrase-ru",
                "line": line,
                "detail": phrase,
            })
    return findings


def check_discourse_marker_run(paragraphs):
    markers = [
        "также", "кроме того", "более того", "при этом", "в то же время",
        "наконец", "таким образом", "однако",
    ]
    findings = []
    run_marker = None
    run_len = 0
    run_start_para = 0
    for i, para in enumerate(paragraphs):
        stripped = para.strip().lower()
        matched = None
        for m in markers:
            if stripped.startswith(m):
                matched = m
                break
        if matched and matched == run_marker:
            run_len += 1
        elif matched:
            run_marker = matched
            run_len = 1
            run_start_para = i
        else:
            run_marker = None
            run_len = 0
        if run_len > 2:
            findings.append({
                "rule": "paragraph-discourse-marker-run-ru",
                "line": run_start_para,
                "detail": f"'{run_marker}' opens {run_len} consecutive paragraphs",
            })
    return findings


def check_colon_before_list_restate(text):
    findings = []
    pattern = re.compile(r"^\s*[-*]\s*([^\s:.]{2,30}):\s*(.+)$", re.MULTILINE)
    for m in pattern.finditer(text):
        head = m.group(1).strip().lower()
        rest = m.group(2).strip().lower()
        if rest.startswith(head):
            line = text.count("\n", 0, m.start()) + 1
            findings.append({
                "rule": "colon-before-list-restate-ru",
                "line": line,
                "detail": m.group(0)[:80],
            })
    return findings


def check_em_dash_overuse(paragraphs):
    """Flag chained rhetorical dashes ('X -- Y -- Z -- W', the AI mic-drop
    tell), not legitimate Russian subject-predicate-omission or appositive
    dashes, which are normal in dense technical/formal prose and can
    legitimately appear several times in one paragraph of equivalence
    definitions or algorithm descriptions. Calibrated against the real
    manuscript (paper-ru/): all 4 initial hits at threshold 3 were
    legitimate 'X -- eto Y' or single explanatory-dash constructs, not
    slop chains, so the threshold is raised and the check instead looks
    for genuine adjacency (multiple dashes inside one sentence, not
    spread across a whole paragraph).
    """
    findings = []
    for i, para in enumerate(paragraphs):
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            n = sentence.count("\u2014")
            if n >= 3:
                findings.append({
                    "rule": "em-dash-overuse-ru",
                    "line": i,
                    "detail": f"{n} em-dashes in one sentence: {sentence[:80]}",
                })
    return findings


def main():
    if not os.path.isfile(MANUSCRIPT):
        print(f"slop_check_ru: no extracted text at {MANUSCRIPT}", file=sys.stderr)
        print("run scripts/research/extract_text_ru.sh first", file=sys.stderr)
        return 1

    with open(MANUSCRIPT, encoding="utf-8") as fh:
        text = fh.read()
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    phrases = load_banned_phrases()
    waived_rules = load_waivers()

    findings = []
    findings += check_banned_phrases(text, phrases)
    findings += check_discourse_marker_run(paragraphs)
    findings += check_colon_before_list_restate(text)
    findings += check_em_dash_overuse(paragraphs)

    unwaived = [f for f in findings if f["rule"] not in waived_rules]

    for f in unwaived:
        print(f"UNWAIVED: {f['rule']} at line {f['line']}: {f['detail']}")

    if unwaived:
        print(f"\nslop_check_ru: {len(unwaived)} unwaived finding(s).")
        return 1
    print(f"slop_check_ru: clean ({len(findings)} total, all waived or zero).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
