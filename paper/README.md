# Manuscript sources

The active section order is defined by main.tex. The Russian manuscript in
../paper-ru uses the same table, figure, bibliography, and numerical sources.

## Build

From the repository root:

```sh
make paper paper-ru
make audit
make audit-ru
```

Build scripts first run the original release integrity check, then generate
the current approach-centered tables with analysis/build_approach_tables.py.
Tectonic compiles the manuscripts only after generation succeeds.

## Current structure

Problem and research questions; formal context policies and algorithms;
Methods; history retention; hybrid state; update protocol and schema;
resources and economics; limitations; related work; conclusion; metric and
trajectory-length appendices.

Measured claims in the prose use generated/approaches.tex. All new-* tables
and new-* plot datasets are generated from canonical run data or the final
hybrid aggregates. Generated files must not be hand-edited.

Architecture figures retain the original visual language, but correct
unverified reasoning-retention claims and show both components of hybrid
state. Algorithms specify information flow and the inline reference
contract; they do not claim to reconstruct unavailable implementation traces.

Tables and captions remain English in both manuscripts. Old result sections,
old diagrams not included by main.tex, and the historical composition
generator are archival material, not current results.
