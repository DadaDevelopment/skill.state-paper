"""Validate the active EN/RU paper graph and its reader-facing contract.

The graph follows actual inputs rather than a stale filename allowlist. The
supported wrapper form is a one-argument command whose body is an input, as
used by sharedtable/sharedfigure. Missing or unresolved inputs always fail.
Run with --rendered after both prose-extraction targets to check their text too.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE_IDS = re.compile(r"\b(?:E\s*[-.]?\s*1|V\s*[-–—]?\s*axis|rungs?)\b", re.I)
COUNTS = re.compile(r"(?<![\d.])(?:87|174|261|1044|1392)(?![\d.])")
RAW_FRACTION = re.compile(r"(?<!\d)\d{2,}\s*/\s*\d{2,}(?!\d)")
COUNT_HEADERS = re.compile(r"\b(?:pairs|solved\s*/\s*runs|control\s+only|rung\s+only|runs\s*/\s*condition)\b", re.I)
AI_SECTION = re.compile(r"(?:Использование\s+ИИ|Use\s+of\s+AI|AI\s+(?:use|assistance|disclosure)|Artificial\s+intelligence\s+(?:use|assistance))", re.I)


class GraphError(ValueError):
    pass


def blank(text):
    return "".join("\n" if char == "\n" else " " for char in text)


def strip_comments(source):
    """Preserve offsets and escaped percent signs while hiding TeX comments."""
    chars = list(source)
    for line in re.finditer(r"[^\n]*(?:\n|$)", source):
        for offset, char in enumerate(line.group()):
            if char != "%":
                continue
            pos = line.start() + offset
            backslashes, index = 0, pos - 1
            while index >= 0 and source[index] == "\\":
                backslashes += 1
                index -= 1
            if backslashes % 2 == 0:
                stop = source.find("\n", pos)
                if stop == -1:
                    stop = len(source)
                chars[pos:stop] = " " * (stop - pos)
                break
    return "".join(chars)


def group(source, start, opener="{", closer="}"):
    if start >= len(source) or source[start] != opener:
        raise GraphError(f"Expected {opener!r} near {source[start:start + 60]!r}")
    depth, index = 1, start + 1
    while index < len(source):
        if source[index] == "\\":
            index += 2
            continue
        if source[index] == opener:
            depth += 1
        elif source[index] == closer:
            depth -= 1
            if depth == 0:
                return source[start + 1:index], index + 1
        index += 1
    raise GraphError("Unclosed LaTeX group in active manuscript")


def whitespace(source, index):
    while index < len(source) and source[index].isspace():
        index += 1
    return index


def mask_commands(source, names):
    """Mask just command calls/arguments, retaining unrelated text and lines."""
    masked = list(source)
    pattern = re.compile(r"\\(" + "|".join(sorted(names, key=len, reverse=True)) + r")(?![A-Za-z])\*?")
    for match in pattern.finditer(source):
        index = whitespace(source, match.end())
        while index < len(source) and source[index] == "[":
            _, index = group(source, index, "[", "]")
            index = whitespace(source, index)
        if index < len(source) and source[index] == "{":
            _, index = group(source, index)
            masked[match.start():index] = blank(source[match.start():index])
    return "".join(masked)


def input_graph(main):
    """Resolve TeX inputs relative to the compilation working directory."""
    main = Path(main).resolve()
    if not main.is_file():
        raise GraphError(f"Missing manuscript entry point: {main}")
    workdir = main.parent
    wrappers, visited, stack = {}, [], []

    def visit(path):
        path = path.resolve()
        if not path.is_file():
            raise GraphError(f"Missing active input: {path}")
        if path in stack:
            raise GraphError("Cyclic manuscript inputs: " + " -> ".join(str(p) for p in stack + [path]))
        if path in visited:
            return
        visited.append(path)
        stack.append(path)
        source = strip_comments(path.read_text(encoding="utf-8"))
        index = 0
        while index < len(source):
            match = re.search(r"\\([A-Za-z]+)\*?", source[index:])
            if not match:
                break
            start = index + match.start()
            index += match.end()
            command = match.group(1)
            if command in {"newcommand", "renewcommand", "providecommand"}:
                index = whitespace(source, index)
                name, index = group(source, index)
                index = whitespace(source, index)
                arguments = "0"
                if index < len(source) and source[index] == "[":
                    arguments, index = group(source, index, "[", "]")
                    index = whitespace(source, index)
                default_argument = False
                if index < len(source) and source[index] == "[":
                    _, index = group(source, index, "[", "]")
                    index = whitespace(source, index)
                    default_argument = True
                body, index = group(source, index)
                wrapper = re.fullmatch(r"\s*\\(?:input|include)\s*\{([^{}]+)\}\s*", body)
                if wrapper and arguments == "1" and not default_argument:
                    wrappers[name.lstrip("\\")] = wrapper.group(1)
                elif re.search(r"\\(?:input|include)\b", body):
                    raise GraphError(f"Unsupported input-wrapper definition {name} in {path}")
                continue
            if command not in {"input", "include", "sharedtable", "sharedfigure"} and command not in wrappers:
                continue
            index = whitespace(source, index)
            if index >= len(source) or source[index] != "{":
                raise GraphError(f"Braced input required in {path} near offset {start}")
            argument, index = group(source, index)
            if command not in {"input", "include"}:
                if command not in wrappers:
                    raise GraphError(f"Undefined input wrapper \\{command} in {path}")
                argument = wrappers[command].replace("#1", argument)
            if "\\" in argument or "#" in argument:
                raise GraphError(f"Unresolved active input {argument!r} in {path}")
            target = workdir / argument
            if not target.suffix:
                target = target.with_suffix(".tex")
            visit(target)
        stack.pop()

    visit(main)
    return tuple(visited)


def active_graphs(root=REPO):
    root = Path(root)
    return {language: input_graph(root / directory / "main.tex") for language, directory in
            (("EN", "paper"), ("RU", "paper-ru"))}


def line_number(text, position):
    return text.count("\n", 0, position) + 1


def visible_source(path):
    source = strip_comments(path.read_text(encoding="utf-8"))
    return mask_commands(source, {"input", "include", "sharedtable", "sharedfigure", "label", "ref", "eqref", "cite", "citep", "citet", "citealp", "citealt"})


def source_findings(root=REPO):
    root = Path(root)
    findings = []
    for language, graph in active_graphs(root).items():
        count_paragraphs = set()
        for path in graph:
            is_section = "sections" in path.parts
            is_table = "tables" in path.parts
            if not (is_section or is_table):
                continue
            source = visible_source(path)
            relative = path.relative_to(root)
            for pattern, reason in ((SOURCE_IDS, "internal study/rung identifier"),
                                    (RAW_FRACTION, "raw outcome fraction"),
                                    (COUNT_HEADERS, "count/discordance-only reader column"),
                                    (AI_SECTION, "removed AI-use section")):
                for match in pattern.finditer(source):
                    findings.append(f"{relative}:{line_number(source, match.start())}: {reason}: {match.group()!r}")
            for match in COUNTS.finditer(source):
                if is_section and path.name == "04_setup.tex":
                    paragraph = len(re.split(r"\n\s*\n", source[:match.start()]))
                    count_paragraphs.add((path, paragraph))
                else:
                    findings.append(f"{relative}:{line_number(source, match.start())}: sample-size accounting outside the single Methods paragraph: {match.group()}")
            if is_table and re.search(r"[А-Яа-яЁё]", source):
                findings.append(f"{relative}: shared reader table contains Cyrillic text")
        if len(count_paragraphs) > 1:
            findings.append(f"{language}: sample-size accounting occurs in {len(count_paragraphs)} Methods paragraphs; maximum is one")
    return findings


def rendered_findings(root=REPO):
    root = Path(root)
    findings = []
    for filename in ("manuscript.txt", "manuscript-ru.txt"):
        path = root / "build/research" / filename
        if not path.is_file():
            raise GraphError(f"Required extracted manuscript is missing: {path}")
        source = path.read_text(encoding="utf-8")
        if not source.strip():
            raise GraphError(f"Required extracted manuscript is empty: {path}")
        for pattern, reason in ((SOURCE_IDS, "internal study/rung identifier"), (RAW_FRACTION, "raw outcome fraction"),
                                (COUNT_HEADERS, "count/discordance-only reader column"), (AI_SECTION, "removed AI-use section")):
            for match in pattern.finditer(source):
                findings.append(f"{path.relative_to(root)}:{line_number(source, match.start())}: {reason}: {match.group()!r}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rendered", action="store_true", help="also require and inspect both extracted manuscripts")
    args = parser.parse_args()
    try:
        findings = source_findings()
        if args.rendered:
            findings += rendered_findings()
    except (GraphError, OSError) as error:
        print(f"manuscript_contract: {error}", file=sys.stderr)
        return 1
    for finding in findings:
        print(finding)
    if findings:
        print(f"manuscript_contract: {len(findings)} violation(s)")
        return 1
    suffix = " and both extracted manuscripts" if args.rendered else ""
    print(f"manuscript_contract: active EN/RU source graphs{suffix} satisfy the reader contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
