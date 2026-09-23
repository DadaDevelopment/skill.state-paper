#!/bin/sh
set -eu

cd "$(dirname "$0")/../.."

mkdir -p build/research
python3 scripts/research/manuscript_contract.py

if [ ! -d paper-ru ]; then
  echo "extract_text_ru: paper-ru/ does not exist yet - nothing to extract" >&2
  exit 1
fi

echo "==> expanding LaTeX includes (RU)"
(cd paper-ru && latexpand main.tex) > build/research/manuscript-ru.expanded.tex

echo "==> converting to plain text (RU)"
pandoc \
  -f latex \
  -t plain \
  build/research/manuscript-ru.expanded.tex \
  -o build/research/manuscript-ru.txt

python3 scripts/research/prose_only.py \
  build/research/manuscript-ru.expanded.tex build/research/manuscript-ru-prose.tex
pandoc -f latex -t plain build/research/manuscript-ru-prose.tex \
  -o build/research/manuscript-ru-prose.txt

WORDS=$(wc -w < build/research/manuscript-ru.txt)
echo "==> extracted ${WORDS} words"

if [ "$WORDS" -le 2000 ]; then
  echo "extract_text_ru: manuscript-ru.txt has only ${WORDS} words - looks empty or truncated" >&2
  exit 1
fi

if ! grep -qi "введение\|Введение" build/research/manuscript-ru.txt; then
  echo "extract_text_ru: no 'Введение' section header found - extraction likely broke the structure" >&2
  exit 1
fi

echo "==> sanity checks passed"
