#!/bin/sh
set -eu

cd "$(dirname "$0")/../.."

mkdir -p build/research
python3 scripts/research/manuscript_contract.py

echo "==> expanding LaTeX includes"
(cd paper && latexpand main.tex) > build/research/manuscript.expanded.tex

echo "==> converting to plain text"
pandoc \
  -f latex \
  -t plain \
  build/research/manuscript.expanded.tex \
  -o build/research/manuscript.txt

# Keep tables in the full extraction for the reader-contract audit. Prose
# linting instead receives prose plus captions, not graphical syntax or rows.
python3 scripts/research/prose_only.py \
  build/research/manuscript.expanded.tex build/research/manuscript-prose.tex
pandoc -f latex -t plain build/research/manuscript-prose.tex \
  -o build/research/manuscript-prose.txt

WORDS=$(wc -w < build/research/manuscript.txt)
echo "==> extracted ${WORDS} words"

if [ "$WORDS" -le 2000 ]; then
  echo "extract_text: manuscript.txt has only ${WORDS} words - looks empty or truncated" >&2
  exit 1
fi

if ! grep -qi "introduction" build/research/manuscript.txt; then
  echo "extract_text: no 'introduction' found - extraction likely broke the structure" >&2
  exit 1
fi

echo "==> sanity checks passed"
