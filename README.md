# Bounded Context Is Not Bounded Information

Materials for the paper testing whether structured state memory (SKILL.state,
arXiv:2608.26263) transfers from synthetic long-horizon benchmarks to real
coding tasks.

Short answer: it does not. On 1044 runs the method as published solves 0.349 of
tasks against 0.613 for a transcript control, and the deficit grows with task
horizon rather than shrinking.

## Building the paper

```
sh paper/build.sh
```

This runs the analysis first and typesets second, in that order and for a
reason: every table, every figure coordinate and every inline number in the
manuscript is generated from the released run data. No measured number is
written into the LaTeX source. The analysis also enforces an integrity gate
that recomputes the published headline values and aborts the build on any
mismatch, so a stale table cannot survive a change in the data.

Requires `tectonic` (self-contained, fetches its own packages) and Python 3
with no third-party dependencies. The statistics are stdlib only, including the
exact McNemar and sign tests, so the analysis runs anywhere Python does.

## Layout

| path | what |
|---|---|
| `paper/` | manuscript: `main.tex`, `sections/`, `figures/`, generated `tables/` |
| `analysis/build_paper.py` | the deterministic analysis and the integrity gate |
| `data/e1-release/` | the released dataset: canonical CSV, raw JSONL, data dictionary |
| `data/e1-dataset-1044.tar.gz` | the same release, packaged |
| `results/` | standalone result notes, including the two retractions |
| `design/` | pre-registration and design specifications |
| `docs/` | extraction of the original paper under test |

## The study

87 Terminal-Bench 2.0 tasks, 4 conditions, 3 independent trials, every cell
filled. The conditions differ in one property: how many recent exchanges are
retained verbatim beside the model-maintained state block (k = 0, 2, 6), plus a
full-transcript control carrying no state block.

Verdicts come only from each task's own verifier. A run without an external
verdict does not enter a results table.

The design was fixed in writing before the series ran, and the pre-registered
hypothesis about cost amortising on long horizons was refuted by the data. It
is reported as a refutation rather than dropped.

## Extending to V2

The composition study (which facts a runtime state must carry) is still being
measured. Section 10 is written but gated:

- `\vtwofalse` in `paper/preamble.tex` compiles the stub, which states the
  design and the pre-registered prediction and contains no numbers.
- `\vtwotrue` compiles `sections/09_results_composition.tex`, which carries a
  block explaining exactly which tables to generate and where they go.

## Status

The manuscript is a working draft. Authors, affiliation and venue are not yet
filled in; the title page carries a placeholder note where they belong.
