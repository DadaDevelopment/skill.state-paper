# paper/ - the manuscript

Build:

    sh paper/build.sh          # regenerates numbers, then typesets
    # or, if you only touched prose:
    cd paper && /opt/data/bin/tectonic main.tex

`build.sh` runs the analysis first and **fails the build** if the recomputed
numbers disagree with the published release. That gate is the point: the PDF
cannot be built from stale tables.

## The rule that keeps this honest

**No measured number is typed into a section file.** Every figure in the prose
is a macro defined in `generated/numbers.tex`, which is written by
`analysis/build_paper.py` from `data/e1-release/canonical-e1-full.csv`.

To use a number in the text, add it to the builder and reference the macro. If
you find yourself typing `2.57` into a `.tex` file, stop - that number will not
update when the data does, and nothing will warn you.

## Layout

```
main.tex              master file, section order, extension switches
preamble.tex          packages, house macros, \ifvtwo / \ifetwo switches
references.bib        bibliography
build.sh              analysis + typeset, with the integrity gate
sections/             one file per section
tables/               GENERATED - complete tabular environments, do not edit
generated/numbers.tex GENERATED - inline macros, do not edit
```

Both generated directories are rewritten on every build. Edits there are lost.

## Source tags

Claims about our own system carry a tag, and the reader is told so in the
abstract:

- `\live` - measured on a real run
- `\code` - a property of the code
- `\origin` - a statement of the original papers

Untagged text is argument, not evidence. Keep it that way.

## Adding the V2 results (composition ladder)

The slot already exists. While `\vtwofalse` (the default in `preamble.tex`),
`main.tex` typesets `sections/09_results_composition_stub.tex`, which states
the design and the pre-registered prediction and contains no numbers. To bring
in the real section:

1. Close the trial set on the stand.
2. Write `analysis/build_composition.py` on the model of `build_paper.py`. It
   must emit complete tabulars into `paper/tables/`:
   - `v1_ladder_solve.tex` - solve rate per rung plus control
   - `v2_ladder_paired.tex` - paired McNemar against the control
   - `v3_ladder_cost.tex` - cost/peak/output on both-solved pairs
   - `v4_ladder_redundancy.tex` - redundant-inspect fraction per rung

   and append its macros to `generated/numbers.tex`.
3. Set `\vtwotrue` in `preamble.tex`.
4. Fill the `\pending{}` blocks in `sections/09_results_composition.tex` with
   the sentences the data supports, and delete the ones that no longer apply.

The same pattern is wired for the schema x protocol matrix: `\ifetwo` guards
`sections/10_results_schema_protocol.tex`, which does not exist yet - create it
and flip the switch.

Note that macro names cannot contain digits (LaTeX restriction). The builder
converts them to words, so the key `CostRatioTail0` becomes the command
`\CostRatioTailZero`. Follow that convention in any new builder.

## Draft notes

`\note{...}` (red) and `\pending{...}` (blue) render while
`\draftnotestrue`. Set `\draftnotesfalse` in `preamble.tex` for submission;
both then vanish without touching the text around them.
