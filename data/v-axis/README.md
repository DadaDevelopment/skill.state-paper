# Exploratory runtime-memory composition records

`vaxis-trial1.jsonl` is a historical first-repeat export. The revised paper uses
only the complete, task-aligned `control`, `hybrid-v1`, `hybrid-v3`, `hybrid-v6`,
and `hybrid-v7` arms for a separate descriptive composition comparison. The
generator `analysis/build_composition_exploratory.py` validates unique records,
equal task coverage, model/schema/history settings, numeric finiteness and the
normalized tariff. Incomplete inline records and the schema comparison are not
used in this exploratory table; their final evidence comes from
`data/followup-final/arm-summary.csv`.

The file-only and files/changes/commands configurations were not continued into
the second repeat after preliminary results. This selection makes the restored
comparison exploratory. It does not make the already completed first-repeat
records invalid, and it does not justify pooling the discontinued configurations
with the final two-repeat release. The control and richer memory rows are the
first-repeat component of that release, **not independent replications**. The
overlapping success margins are checked in the research tests; raw second-repeat
records are not available here for a task-level identity check.

The source identifiers have the following reader-facing meanings, cumulative
within the memory configurations:

| Source identifier | Runtime-owned information |
|---|---|
| `control` | Full interaction history; no structured state |
| `hybrid-v1` | File references |
| `hybrid-v3` | File references, modifications, and command records |
| `hybrid-v6` | Above, plus diagnostics, environment, and test records |
| `hybrid-v7` | Above, plus failed-attempt records |

Several components were added together. Differences between these rows are
not isolated effects of commands, diagnostics, or tests. Coverage-related
counters in this export are not used as measurements of memory completeness.

The main composition table reports all retained outcomes. Success-conditioned
cost ratios appear only in the sensitivity table, which distinguishes each
condition's own joint-success subset from the fixed task intersection solved
by every selected configuration. Each entry is a median of within-task ratios
against the full-history control, not a ratio of aggregate medians. No new
inferential significance test is attached to this selected comparison.

Costs are normalized at USD 0.15 / 0.03 / 0.50 per million uncached input /
cached input / output tokens. Per-record costs in the source are rounded to
six decimals; medians and efficiencies use those recorded amounts. They are
not provider invoices.
