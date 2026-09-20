# Redundant tool work: the mechanism of information loss (RQ3)

Measured 2026-09-14. Generator `tools/redundant_work.py`, canonical dataset
`data/canonical-runs.csv`.

## What is measured

    repetition = total tool calls / distinct (tool, arguments) pairs

A run that never repeats an action scores 1.00. The quantity is deliberately
crude: it needs no judgement about what the agent "meant", only whether it
issued a byte-identical call again.

The read-only subset (`read`, `grep`, `glob`, `list`) is reported separately,
because re-running a test after an edit is legitimate repetition whereas
re-reading an unchanged file is not.

**Experimental unit:** one run. **Aggregation:** per-task comparison against the
control of the SAME trial; exact two-sided sign test over tasks.

---

## Result 1: terminal-bench-2.0, complete matrix, 216 runs, 3 trials

Paired sign test, repetition of each condition against its same-trial control:

| condition | higher than control | lower | equal | p |
|---|---|---|---|---|
| **State-only** | **25** | 1 | 10 | **<0.0001** |
| **State + 2** | **21** | 2 | 13 | **0.0001** |
| State + 6 | 11 | 6 | 19 | 0.33 |
| State + 12 | 6 | 6 | 24 | 1.00 |
| State + transcript | 4 | 5 | 27 | 1.00 |

Median repetition: control 1.00, state-only 1.27, state+2 1.06, and 1.00 for
every wider condition.

This is the first effect in this project that is both **statistically
significant** and **monotone in the independent variable**, on a completed
design rather than a partial one. It decays exactly where the axis predicts: two
retained messages still show it, six do not.

The effect is significant but small in magnitude on this corpus: a median
repetition of 1.27 means roughly one call in four is a re-fetch.

---

## Result 2: terminal-bench-4.0 pilot - the same mechanism, an order larger

**Status: `preview only`.** The design is not complete (11 runs, 6 tasks, one
trial, two conditions). No claim is made from it; it is reported because it
shows the same mechanism at a magnitude the completed corpus cannot reach.

| task | condition | calls | distinct | repetition | most repeated call |
|---|---|---|---|---|---|
| mvcc-lsm-compaction | control | 27 | 26 | 1.04 | 2x read regression_test.cc |
| mvcc-lsm-compaction | state-only | 707 | 45 | **15.71** | **97x read flush_builder.cc** |
| batched-eval-parity | control | 74 | 71 | 1.04 | 3x bash test |
| batched-eval-parity | state-only | 609 | 118 | **5.16** | **143x read evaluate.py** |
| music-harmony | control | 47 | 46 | 1.02 | 2x bash |
| music-harmony | state-only | 225 | 54 | **4.17** | **164x read page0.png** |
| ontology-kg-querying | control | 54 | 54 | 1.00 | - |
| ontology-kg-querying | state-only | 397 | 168 | 2.36 | 47x read ontology_network |

Median repetition: control **1.02**, state-only **3.26**.

On read-only calls alone, state-only reaches 56x on `music-harmony` and 26x on
`mvcc-lsm-compaction`.

---

## Why the same mechanism differs by an order of magnitude between corpora

The measured difference between corpora is large and has a plain explanation
supported by two already-measured quantities:

- terminal-bench-2.0 control runs take a median of 11 model calls; peak prompt
  utilisation is 5% of the window. There is little history to lose.
- terminal-bench-4.0 control runs take 18-58 calls; peak prompt utilisation
  reaches 66%. There is a great deal to lose, and it is lost.

**HYPOTHESIS**, not established: repetition grows with task horizon, and the
2.0 corpus sits below the horizon where forgetting becomes expensive. This is
exactly the crossover RQ2 predicts, and it is testable on the 89-task corpus by
correlating repetition with control turn count. It is NOT established by the
pilot, which has one trial and six tasks.

---

## Consequence for the turn budget

On terminal-bench-4.0, state-only hit the 200-call budget in **5 of 6** runs;
the control hit it **0 of 5** times and stopped on its own after 18-58 calls.

A run stopped by the budget has no verdict about capability - it was cut off. So
budget-stopped runs are excluded from cost aggregation and counted separately,
which design E1 already pre-declares as an artefact trap. The pilot shows the
trap is real and not hypothetical: without that exclusion, state-only would look
*cheaper* per solved task on long horizons purely because it was stopped before
finishing.

---

## Verification performed

Both trajectories of `mvcc-lsm-compaction` were opened by hand and the repeated
calls listed directly from the session JSONL before the metric was written:
control issued 27 calls of which 26 were distinct; state-only read
`/app/src/flush_builder.cc` 97 times, `/app/src/snapshot_context.cc` 97 times,
and two headers 92 times each.

The metric was then written to reproduce that reading mechanically, not the
reverse.
