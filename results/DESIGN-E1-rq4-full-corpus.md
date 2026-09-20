# Experiment design E1: RQ4 on the full terminal-bench-2.0 corpus

Pre-registered. Written before any run of this series. Nothing in this file may
be changed after the first run starts; deviations are recorded as amendments
with timestamps, below.

The paper's four claims against SKILL.state are:

- **RQ1** schema sensitivity
- **RQ2** short-horizon overhead / horizon crossover
- **RQ3** irreversible information loss
- **RQ4** token reduction is not cost reduction under prompt caching

**This series addresses RQ4 and RQ2, and nothing else.** RQ1 and RQ3 require
interventions not built yet and have their own designs.

---

## 1. Question

Under a production prompt-caching regime, does replacing the transcript with a
maintained state block reduce the cost of completing a task, and does the answer
depend on task horizon?

## 2. Hypotheses

**H0 (RQ4):** the cost ratio of state-only to transcript control has median 1.0
- discarding the transcript neither raises nor lowers billed cost.

**H1 (RQ4):** the median cost ratio is greater than 1.0 - state-only costs more
than the control despite a smaller prompt.

**H0 (RQ2):** the cost ratio does not vary with task horizon.

**H1 (RQ2):** the cost ratio decreases as horizon grows, crossing 1.0 at some
horizon - the overhead is amortised on long tasks.

RQ4 is directional and one-sided by construction: the prior measurement on 12
tasks put the ratio at 1.94-2.35 across three trials. This series tests whether
that survives the full corpus.

## 3. Intervention

The context assembled for each model call:

- **Control:** full conversation transcript, no state block. Unmodified agent.
- **Treatment (state-only):** state block replaces the transcript entirely. This
  is SKILL.state as published (arXiv:2608.26263).
- **Treatment (state + N):** state block plus the N most recent messages,
  N in {2, 6, 12}.
- **Treatment (state + transcript):** state block added, nothing removed.

Nothing else differs: same model, schema, tools, turn budget, task, verifier.
`state_tail` is read back out of each run's trace and a run whose realised tail
differs from the requested one is rejected, not analysed.

## 4. Independent variable

Amount of verbatim recent history retained alongside the state block:
`0, 2, 6, 12, infinity` messages, plus the no-state control.

Ordinal, six levels. The control is not a point on this axis - it has no state
block - and is always reported separately.

## 5. Dependent variables

**Primary (RQ4):** `cost_usd`, provider-billed, cache-aware.

**Secondary, mechanism:** `prompt_peak_tokens`, `output_tokens`,
`cache_read_tokens`, `cache_hit_pct`, `turns`.

**Tertiary, reported but not tested here:** `solved`. See section 7.

All are per-run measurements already defined in `data/DATA-DICTIONARY.md`.

## 6. Confounders and how each is controlled

| confounder | control |
|---|---|
| Task difficulty | Paired design: every condition runs every task; comparison is always within task. |
| Run-to-run variance | 3 independent trials per cell; treatment compared to the control **of the same trial**, never to a pooled control. Measured verdict reproducibility is 75%, which is why this is not optional. |
| Provider-side price or cache-policy change | Trials interleaved across conditions rather than run condition-by-condition, so a drift affects all conditions alike. |
| Wall-clock limits censoring expensive conditions | `stop_reason` recorded per run; censored runs excluded from cost aggregation and counted explicitly. |
| Output-ceiling truncation | Recorded as `stop_reason = output_ceiling`, excluded from cost aggregation. |
| Turn-budget exhaustion | Recorded as `stop_reason = turn_budget`, excluded from cost aggregation. |
| Silent condition collapse (a treatment running as control) | `state_tail` verified from the trace; smoke protocol asserts distinct context sizes per level before the series starts. |
| Schema advantage for a specific task | One task-agnostic schema for all tasks and all conditions; schema variation is RQ1, not this series. |

## 7. Sample size and power rationale

**Cost (primary):** continuous, paired per task. The measured effect on 12 tasks
was a median ratio of 1.94-2.35 with IQR roughly 1.0-3.1. A sign test on paired
per-task ratios needs 6 tasks in one direction for p < 0.05; the observed
direction was consistent on the large majority of tasks. **89 tasks is far above
requirement for the cost claim.**

**Solve rate (tertiary):** McNemar exact requires **6 discordant tasks**, and
the measured discordance rate is **0.08**, giving a requirement of **72 tasks**
(`results/POWER.txt`). 89 tasks clears it, but only just, and only if
discordance is one-sided. Solve rate is therefore reported with its interval and
explicitly labelled underpowered unless the observed discordance exceeds 6.

**Corpus:** all 89 terminal-bench-2.0 tasks. Every task is feasible on the stand
(`data/corpus-census.csv`), so there is no selection step and no selection bias.

## 8. Stopping rule

The series stops when all planned cells have a verdict or a recorded
`stop_reason`. **No analysis and no claim before that point**; partial data is
`preview only`.

Planned cells: 89 tasks x 6 conditions x 3 trials = **1602 runs**.

Two exceptions, both pre-declared:

1. **Budget stop.** If projected cost exceeds $40 (measured median cell cost
   $0.0061 gives an estimate of $9.8; the ceiling is 4x that), the series stops
   and reports how far it got. The estimate is re-checked after every 200 runs.
2. **Stack-invalidity stop.** If the smoke protocol fails at any point, every
   run made after the last passing smoke is discarded, not analysed.

A stalled run (no agent output for 30 minutes, `tools/detect_stalled_run.py`) is
killed and **re-queued once**; a cell that stalls twice is recorded with
`stop_reason = infrastructure` and excluded.

## 9. Statistical tests

| claim | test | why |
|---|---|---|
| Cost ratio differs from 1.0 | Exact two-sided sign test on paired per-task ratios (treatment vs same-trial control) | Ratios are not normal and the sample has heavy tails; the sign test assumes neither. |
| Cost ratio varies with horizon (RQ2) | Spearman rank correlation between control turn count and per-task cost ratio | Monotonic trend without assuming a functional form. |
| Solve-rate difference | McNemar exact, two-sided | Paired binary data; only discordant tasks are informative. |
| Trial agreement | Reported as raw agreement fraction, no test | A descriptive reliability figure, not a hypothesis. |

Medians reported with IQR over tasks. **No p-value is computed on a partial
dataset**, and no test is chosen after seeing the data.

## 10. Result that would support the hypotheses

**RQ4 supported if:** the paired sign test on cost ratios for state-only versus
control gives p < 0.05 with median ratio > 1.0, in **each of the three trials
independently**, and the mechanism holds in hand-checked trajectories - cache
read flat under state-only against growing under control, with higher output
tokens.

**RQ2 supported if:** Spearman correlation between horizon and cost ratio is
negative with p < 0.05, and the fitted trend crosses 1.0 within the observed
horizon range.

## 11. Result that would refute them

**RQ4 refuted if:** the median cost ratio is <= 1.0, or the sign test does not
reach significance, or the direction is inconsistent across the three trials.
Any of these means the 12-task finding did not survive the full corpus and the
claim is dropped from the paper.

**RQ2 refuted if:** the Spearman correlation is not significant, or is positive,
or the trend never approaches 1.0 within the observed range. Then the overhead
does not amortise with horizon and no crossover is claimed.

A specific pre-declared trap: if state-only shows a **lower** cost ratio on long
tasks purely because long tasks are where it more often hits the turn budget and
stops early, that is an artefact, not a crossover. Runs with
`stop_reason = turn_budget` are excluded from cost aggregation for exactly this
reason, and their count per horizon stratum is reported alongside.

---

## Budget and schedule

| quantity | value | source |
|---|---|---|
| runs | 1602 | design |
| measured median cell cost | $0.0061 | `data/canonical-runs.csv` |
| estimated cost | ~$10 | 1602 x 0.0061 |
| measured throughput | 8.5 runs/hour at parallelism 3 | `tools/throughput.py` over the 216-run matrix |
| estimated wall-clock | ~188 hours | 1602 / 8.5 |

**Wall clock is the binding constraint, not money.** At the current stand this
series takes about eight days.

Parallelism is capped at 3 by stand memory (measured peak 16 GB at parallelism 4
against 15 GB physical), not by the provider - the key tolerates 4-6 concurrent
requests.

This is the one decision requiring the owner: either accept an eight-day series,
or provide a larger stand and additional keys. With 64 GB and two keys the same
series fits in roughly two days.

---

## Amendments

None. Any change after the first run is appended here with a timestamp and a
reason.
