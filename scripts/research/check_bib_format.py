"""Require BibTeX formatting to be idempotent, independent of git staging."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BIB = REPO / "paper/references.bib"


def main():
    before = BIB.read_bytes()
    result = subprocess.run(["npx", "bibtex-tidy", str(BIB), "--duplicates=doi,key,citation", "-m"],
                            cwd=REPO, check=False)
    if result.returncode:
        return result.returncode
    if BIB.read_bytes() != before:
        print("references: bibtex-tidy changed the bibliography; inspect its diff and rerun", file=sys.stderr)
        return 1
    print("references: bibliography formatting is idempotent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
