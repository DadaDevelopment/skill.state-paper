#!/bin/sh
set -eu

cd "$(dirname "$0")/../.."

mkdir -p build/research

. .venv-research/bin/activate

echo "==> checking references.bib against Semantic Scholar / OpenAlex / CrossRef / DBLP / ACL"
refchecker-webui check \
  --paper paper/references.bib \
  --no-llm \
  --check-retractions \
  --check-citation-order \
  --suggest-missing \
  --json \
  > build/research/refcheck-bib.json 2> build/research/refcheck-bib.err || true

echo "==> refcheck complete, see build/research/refcheck-bib.json"
