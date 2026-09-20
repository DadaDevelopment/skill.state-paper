#!/bin/sh
set -eu

cd "$(dirname "$0")/../.."

mkdir -p build/research

echo "==> expanding LaTeX includes"
(cd paper && latexpand main.tex) > build/research/manuscript.expanded.tex

echo "==> converting to plain text"
pandoc \
  -f latex \
  -t plain \
  build/research/manuscript.expanded.tex \
  -o build/research/manuscript.txt

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
