#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -x .venv-research/bin/python3 ]; then
  ANALYSIS_PYTHON=.venv-research/bin/python3
else
  ANALYSIS_PYTHON="${PYTHON:-python3}"
fi
"$ANALYSIS_PYTHON" analysis/build_paper.py --check
"$ANALYSIS_PYTHON" analysis/build_approach_tables.py
"$ANALYSIS_PYTHON" analysis/build_approach_tables.py --check
"$ANALYSIS_PYTHON" analysis/build_composition_exploratory.py
"$ANALYSIS_PYTHON" analysis/build_composition_exploratory.py --check
cd paper-ru
"${TECTONIC:-tectonic}" --keep-logs main.tex
