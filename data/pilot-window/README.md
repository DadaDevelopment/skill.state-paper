# Complete history-window pilot: aggregate-only recovery

This directory recovers the finalized history-window pilot, not a new
experiment and not the larger model-written-state comparison. Its design was
12 Terminal-Bench 2 tasks × 6 approaches × 3 repeats (216 executions). The
source describes task selection as stratified by control turn count and the
model as `zai/glm-5.3-flash`.

## Authoritative retained sources

- `results/TABLES.txt`: finalized absolute medians across all tasks and repeats;
  within-repeat, same-task/same-repeat ratios and their task IQRs for prompt
  peak, dollar cost, output tokens and model calls. These ratios include all
  retained outcomes, not only jointly successful executions.
- `results/RESULT-redundant-work.md`, Result 1 only: descriptive median tool-call
  repetition for this completed pilot. No inferential p-value is imported.

`analysis/build_window_pilot.py` parses these sources and validates complete
conditions, three repeats, ratio IQRs and sample counts. It writes the two CSVs
here, checksums both original sources, and produces the shared English tables,
macros and window-curve figure data. Run it with `--check` to detect stale
artifacts. CSV blank fields are unavailable, never zero.

## What could not be recovered

The original `data/canonical-runs.csv`, its data dictionary and its generators
are referenced by the retained reports but are absent from this repository,
its history, the project reference archives and the inspected local sources.
The `DadaDevelopment/pi-rnd` remote does not resolve with the available account.
The implementation repository `DadaDevelopment/pi-skill-state` contains no
pilot dataset. Accordingly, these outputs preserve reported aggregates and do
not claim to recompute episode-level measurements.

The finalized report intentionally omits success rates. Earlier two-repeat
log counts treat a task as successful if a repeat succeeds; they are not
per-execution solved rates, and their relationship to all finalized verdicts
cannot be reconstructed. They are excluded from the tables. Solved rate,
Solved/$, input-token medians and the pooled matched-run cost ratio remain
missing. Neither medians nor ratios of separate medians can recover them.
The per-repeat matched cost ratios are shown separately with their actual
estimand; they are not averaged to fill the pooled-ratio column.

Cache percentages are the finalized report's **reported median cache-hit
percentages**. Missing episode counters and dictionary prevent independently
checking their denominator against `K/(U+K)`. Do not silently give them the
stronger provenance of the independently recomputed cache-hit rates in the
larger comparison. Dollar figures likewise remain reported source costs at
their reported precision; the absent counters preclude re-pricing or checking
the tariff. They are not provider invoices.

## Conditions and admissible interpretation

`tailinf` means **model-written state plus full transcript**. It is not the
no-state full-history control. The retained table calls finite windows `msgs`;
the exact raw-message/complete-exchange selection behavior of this historical
pilot cannot be independently audited without its runtime checkout. Describe
them as the reported history-window settings, not a token budget or a proven
semantic dependence length.

The full curve supports three descriptive observations. Median exact tool-call
repetition reaches its floor at `k=6` and remains there at `k=12` and unbounded
history. Increasing the window beyond six raises median prompt size; prompt
peak ratios exceed the no-state control at `k=12` and unbounded history in
every repeat. Model calls and output still change, and cost rankings fluctuate:
there is no measured cost plateau or demonstrated interior optimum.

Equal repetition medians are not equal trajectories, equal solved-task sets,
or statistical equivalence. This selected small pilot cannot establish a
universal six-step memory horizon. Repeating a byte-identical tool call can be
legitimate after environment changes, so the metric supports a mechanism
hypothesis rather than proving that every repeated call is forgetting.

The repetition report's old sign tests treat task-repeat cells as if they were
independent tasks; they are not reproduced. Its approximation that 1.27 calls
per distinct call means one in four calls is repeated is also not copied:
the corresponding repeated-call share would be `1 - 1/1.27`, about 21%, and is
not itself a directly reported median of per-execution shares.

Partial earlier snapshots, the retracted timeout diagnosis, the withdrawn
interior-optimum claim, and the incomplete separate benchmark preview are not
admitted. Their correction history belongs in the source ledger, not the
manuscript narrative.
