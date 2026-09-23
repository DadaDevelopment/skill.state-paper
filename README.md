# When Structured State Replaces Interaction History

Empirical study of context policies for a terminal-based coding agent.
The manuscript compares recent-history retention, model-written and hybrid
memory, update protocols, state schemas, and resource use. It studies a
transfer of the SKILL.state runtime idea, not a reproduction of its original
experiments.

## Manuscripts

- [English PDF](paper/main.pdf) and [LaTeX](paper/main.tex)
- [Russian PDF](paper-ru/main.pdf) and [LaTeX](paper-ru/main.tex)

Both versions use the same generated English tables, architecture diagrams,
algorithms, and plot data. Experimental sample sizes appear once in Methods.
The two separately evaluated policy families retain their own controls.

## Build and audit

Install Tectonic, Python 3.10+, and the analysis dependency NumPy. For a
local manuscript build:

```sh
python3 -m venv .venv-research
.venv-research/bin/pip install numpy
make paper paper-ru
```

Russian typesetting needs Times New Roman/Arial or Liberation Serif/Sans,
plus DejaVu Sans Mono. On Debian/Ubuntu install fonts-liberation and
fonts-dejavu-core.

For the full research audit, additionally install the Python dependencies
listed in requirements-research.txt, the Node packages, Pandoc, latexpand,
and lychee:

```sh
.venv-research/bin/pip install -r requirements-research.txt
npm install
make audit
make audit-ru
```

Reference and link verification require network access. Failed verification
is not treated as a successful audit.

## Evidence and generated material

| Source | Role |
|---|---|
| data/e1-release/ | Canonical execution-level records for model-written memory |
| data/followup-final/ | Final supplied aggregates for hybrid memory and protocol/schema comparisons |
| analysis/build_approach_tables.py | Current tables, inline numbers, bootstrap intervals, and plot data |
| analysis/build_paper.py --check | Preserved integrity checks against the original execution-level release |
| paper/generated/ and paper/tables/ | Generated at build time; shared by both manuscripts |
| scripts/research/ and tests/research/ | Data, numeric-claim, source-contract, prose, reference, and link checks |

The historical single-trial composition generator and unused manuscript
sections remain in the repository for provenance but are not part of the
current manuscript or its evidence. Design documents describe proposed
behavior; they are not substitutes for an execution-source snapshot.

The final hybrid evidence is aggregate-only. It does not support invented
per-call prompt peaks, task-level bootstrap intervals, or token totals
derived from marginal medians. Its rounded aggregate costs yield approximate
cost efficiencies.

## Release

Pushes to main build both PDFs and update the
[latest release](https://github.com/DadaDevelopment/skill.state-paper/releases/tag/latest).
Source archives contain both language trees and the shared analysis inputs;
the Russian manuscript is not a standalone copy of the English tables.
