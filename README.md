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

The manuscript is a working draft.

## Always-current PDF and LaTeX source

Every push to `main` rebuilds both papers and republishes them to a rolling
GitHub Release tagged `latest` (`.github/workflows/publish-pdf.yml`), so you
never need to know which commit is current or run the build yourself:

```
gh release download latest --repo DadaDevelopment/skill.state-paper \
  --pattern '*.pdf' --pattern '*.tar.gz' --clobber
```

or download directly from the releases page:
`https://github.com/DadaDevelopment/skill.state-paper/releases/tag/latest`

That release always carries, rebuilt from the exact commit named in its own
`BUILD_INFO.txt`:

| asset | what |
|---|---|
| `skill-state-paper-en.pdf` | compiled English paper |
| `skill-state-paper-ru.pdf` | compiled Russian paper |
| `paper-en-source.tar.gz` | full `paper/` LaTeX source (sections, figures, tables, generated macros) |
| `paper-ru-source.tar.gz` | full `paper-ru/` LaTeX source |
| `BUILD_INFO.txt` | commit SHA and UTC build timestamp |

This publish workflow only requires the paper to compile - it is independent
of `make audit` below, which additionally checks prose quality, references,
data invariants and literature coverage and is allowed to be red while the
PDF itself is still correct and current.

## Research CI

`research/` and `scripts/research/` implement the verification layer from
the project's own no-manual-numbers rule and the standard set out in
`research/review-rubric.md`: a zero-slop prose gate, a reference checker
against Semantic Scholar/OpenAlex/CrossRef/DBLP/ACL, Pandera data
invariants on the canonical CSV, a literal-number gate on result-bearing
sections, a literature-watch gap check, and a hostile independent-reviewer
protocol. Run the whole thing with:

```
make audit
```

One-time setup (this environment has no system package manager access, so
tools are user-installed rather than apt-installed - see
`.github/workflows/research-ci.yml` for the CI-runner equivalent using
`apt-get`):

```
uv venv .venv-research && source .venv-research/bin/activate
uv pip install pytest pandera pandas pyyaml requests "academic-refchecker[llm,webui]"
npm install --save-dev github:bheijden/slop bibtex-tidy
```

`make audit` is red until every finding in `research/waivers.yml` is either
fixed or has `approved_by` changed from `PENDING_HUMAN_REVIEW` to an actual
name by a human - an agent is never allowed to approve its own waiver. See
`research/waivers.yml` for what is currently pending and why.

`make results` currently fails: the mechanism (`07_results_mechanism.tex`)
and composition (`10_results_composition_v.tex`) sections carry ~20 numbers
typed by hand from an off-pipeline trace classification, predating this
gate. Fixing that means writing the trace-classification numbers into
`analysis/build_paper.py`'s macro output, not editing the gate - it is
correctly failing on a real violation of the project's own rule.
