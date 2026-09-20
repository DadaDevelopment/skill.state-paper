#!/bin/sh
# Rebuild the paper end to end.
#
# Order matters: the analysis regenerates every table and every inline number
# from the canonical run data, and its integrity gate fails the build if those
# recomputed numbers disagree with the published release. Only then is the PDF
# typeset. A paper that compiles from stale tables is worse than one that does
# not compile.
set -eu

cd "$(dirname "$0")/.."

echo "==> regenerating tables and numbers from canonical run data"
python3 analysis/build_paper.py --check

echo "==> regenerating the composition axis from the v-axis run log"
python3 analysis/build_composition.py

echo "==> typesetting"
cd paper
"${TECTONIC:-/opt/data/bin/tectonic}" main.tex

echo
echo "==> done: paper/main.pdf"
ls -la main.pdf
