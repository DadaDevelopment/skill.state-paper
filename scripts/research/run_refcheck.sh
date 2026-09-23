#!/bin/sh
set -eu

cd "$(dirname "$0")/../.."

mkdir -p build/research

. .venv-research/bin/activate

echo "==> checking bibliography metadata, active citation keys, and retraction status"
python3 scripts/research/run_refcheck.py

echo "==> refcheck complete, see build/research/refcheck-bib.json"
