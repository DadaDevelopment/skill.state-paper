"""Remove non-prose environment bodies, retaining captions and prose.

This is an extraction transform, not a waiver: the complete manuscript is
retained separately for the reader-contract audit and PDF validation.
"""
import argparse
import re
from pathlib import Path

from manuscript_contract import blank, strip_comments

NON_PROSE = {"tabular", "tabular*", "tabularx", "longtable", "tikzpicture",
             "algorithmic", "verbatim", "verbatim*", "lstlisting"}
ENVIRONMENT = re.compile(r"\\(begin|end)\s*\{([^{}]+)\}")


def prose_only(source):
    source = strip_comments(source)
    output = list(source)
    stack = []
    start = None
    for match in ENVIRONMENT.finditer(source):
        kind, name = match.groups()
        if kind == "begin":
            stack.append(name)
            if start is None and name in NON_PROSE:
                start = match.start()
        else:
            if not stack or stack[-1] != name:
                raise ValueError(f"Mismatched LaTeX environment: {name}")
            stack.pop()
            if start is not None and not any(env in NON_PROSE for env in stack):
                output[start:match.end()] = blank(source[start:match.end()])
                start = None
    if stack:
        raise ValueError(f"Unclosed LaTeX environment: {stack[-1]}")
    return "".join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    args.target.write_text(prose_only(args.source.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
