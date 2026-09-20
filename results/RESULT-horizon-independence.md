# Can this corpus tell whether redundancy grows with horizon? (RQ2)

**Answer: no.** At n = 12 tasks the question is not resolvable either way. This
file records a negative result about the DESIGN, not about the effect.

Measured 2026-09-14. Generator `tools/horizon_redundancy.py`, tests
`tests/test_horizon_redundancy.py` (10/10), data `data/canonical-runs.csv`.

## The question

The redundancy effect is established on the complete matrix: state-only repeats
tool calls more than its same-trial control on 25 tasks against 1, p < 0.0001
(`results/RESULT-redundant-work.md`). The open question is whether that penalty
is a **constant tax** or something that **grows with task length** - the
crossover RQ2 predicts.

The pilot on the harder corpus suggested growth (median repetition 3.26 there
against 1.27 here), but six tasks and one trial establish nothing.

## Design

| element | choice |
|---|---|
| Experimental unit | one task, medians taken over three independent trials |
| Horizon | median turn count **of the control arm** |
| Redundancy | median tool-call repetition of the state-only arm |
| Test | Spearman rank correlation, permutation p-value, 200 000 shuffles, fixed seed |
| Tasks | 12 |

**Horizon is taken from the control arm, never from the treatment.** Using the
treatment's own turn count would be circular: a run that re-fetches things takes
more turns by construction, so redundancy would predict itself.

Horizon range in this corpus: 5 to 29 median control turns, a spread of 5.8x.

## Detectability, stated before the result

At n = 12 tasks, the smallest correlation this test can resolve at p < 0.05 is

    |rho| >= 0.62

computed by the same permutation test that produces the p-value, not read from a
table for a different test.

## Result

| task | horizon | redundancy (state-only) | redundancy (control) |
|---|---|---|---|
| prove-plus-comm | 5.0 | 1.43 | 1.25 |
| modernize-scientific-stack | 6.0 | 1.29 | 1.00 |
| pytorch-model-recovery | 8.0 | 1.00 | 1.00 |
| regex-log | 8.0 | 1.57 | 1.00 |
| db-wal-recovery | 9.0 | 1.00 | 1.00 |
| fix-git | 10.0 | 1.42 | 1.00 |
| configure-git-webserver | 13.0 | 1.00 | 1.00 |
| overfull-hbox | 15.0 | 1.51 | 1.00 |
| tune-mjcf | 16.0 | 2.00 | 1.00 |
| git-multibranch | 23.0 | 1.00 | 1.00 |
| cobol-modernization | 25.0 | 1.48 | 1.00 |
| crack-7z-hash | 29.0 | 1.12 | 1.00 |

    Spearman rho = +0.030    p = 0.9256    n = 12 tasks

    Verdict printed by the tool: NOT DETECTABLE at this sample size
    (|rho| = 0.03 is below the 0.62 threshold n=12 can resolve).

## Reading

**This corpus cannot answer the question.** That is the whole result, and it is
weaker than "there is no effect".

The distinction matters and this project has already paid for ignoring it twice.
An observed correlation of +0.03 at n=12 is consistent with no relationship AND
consistent with a real relationship of moderate strength; the design cannot
separate them. Reporting it as "redundancy does not grow with horizon" would be
the same error as the retracted internal-optimum claim, dressed differently.

What can be said, with sources:

1. **[live, established]** Redundancy is significantly higher under state-only
   than under the control, on 25 tasks against 1 (p < 0.0001). That result comes
   from the paired sign test on the complete matrix and is unaffected by this
   one.

2. **[live, established]** No monotone horizon relationship is *detectable* on
   terminal-bench-2.0 across a 5.8x horizon range at n = 12 tasks.

3. **HYPOTHESIS, not established:** the crossover may lie beyond this corpus.
   Control runs here peak at 5% of the context window; the pilot on the harder
   corpus reaches 66% and shows redundancy an order of magnitude larger. A
   29-turn task may simply be short.

Note the descriptive pattern, which is NOT a claim: redundancy on the 29-turn
task (1.12) is lower than on the 5-turn task (1.43). With p = 0.93 this is
noise, and it is recorded only so that a future reader does not rediscover it
and mistake it for a finding.

## What this does NOT license

It does not license "state-only is horizon-independent". It licenses exactly
one sentence: **at n = 12 tasks over a 5.8x horizon range, this corpus cannot
resolve whether redundancy grows with horizon.**

Answering it properly needs either the 89-task corpus (more tasks, same context
pressure) or a completed design on the harder corpus (same tasks, real context
pressure). The second is the one that matters, because context pressure is the
mechanism under test - and that is a design decision for E2, not something to
settle by squinting at these twelve numbers.

## Defect found and gated during this measurement

`detectable_rho` first reported a threshold of **0.00**, meaning any correlation
whatsoever would be "detectable" - which would have turned "this corpus cannot
resolve the question" into "there is no effect", the exact class of error this
project has already retracted twice.

Cause: it bisected over "swap k pairs from the ends", assuming that scrambling
more pairs lowers the correlation monotonically. It does not. Measured directly:

| swaps | rho | p |
|---|---|---|
| 0 | +1.000 | significant |
| 1 | +0.154 | not |
| 2 | -0.413 | not |
| 3 | -0.755 | significant |

One swap of the extreme elements already collapses the correlation, so the
bisection converged on a meaningless bound.

Fixed by direct scan over constructed sequences. The fix is held by a test that
was **verified to fail on the old implementation** (threshold 0.00, 9 passed 1
failed) and pass on the new one (threshold 0.62, 10 passed) - a gate, not a
decoration.
