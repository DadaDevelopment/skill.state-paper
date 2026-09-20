# E1 dataset: SKILL.state against a control on Terminal-Bench 2.0

The pre-registered design is **closed**: 87 tasks x 4 conditions x 3 trials =
**1044 runs**, every cell filled. Verified against the raw collector output with
zero mismatches. Every table below is a deterministic function of
`canonical-e1-full.csv` and can be recomputed without rerunning anything:

```
python3 tools/verify_release.py    # design shape + published-vs-raw integrity
python3 tools/build_tables.py      # every table below
```

## Files

| file | what it is |
|---|---|
| `canonical-e1-full.csv` | the dataset - one row per run, 1044 rows, 25 columns, no derived metrics beyond token arithmetic |
| `raw-e1.jsonl` | the raw collector output every row was built from |
| `raw-e1-failures.jsonl` | attempts that yielded no usable verdict and were excluded (187) |
| `raw-e1-quarantined.jsonl` | runs measured under provider saturation, excluded by a pre-declared rule (26) |
| `TABLES.txt` | aggregate tables with full column semantics |
| `stack-lock.txt` | versions and content hashes frozen for this series |

Integrity: every row in the CSV was cross-checked field by field against
`raw-e1.jsonl` (verdict, turns, and all three token counts) - 0 discrepancies
across 1044 rows.

## Design

* **Experimental unit**: one run of one task under one condition in one trial.
* **Corpus**: Terminal-Bench 2.0. 89 tasks are runnable in principle; this
  stand reaches **87** - `qemu-alpine-ssh` and `qemu-startup` fail in apt
  during setup, before the agent starts, on every attempt
  (`log/RESULT-two-tasks-unrunnable-on-this-stand.md`).
* **Conditions**: `baseline` is the unmodified control. `tail0`, `tail2`,
  `tail6` all replace conversation history with a structured state block and
  differ only in how many recent exchanges are kept verbatim alongside it
  (0, 2, 6). This is the single manipulated property; everything else is frozen.
* **Model**: `zai/glm-5.3-flash` throughout.
* **Verdict**: `verdict_reward` comes from the task's own verifier. A run
  without a verifier verdict never enters the dataset - it goes to
  `raw-e1-failures.jsonl`.
* **Trials**: 3 independent repetitions, since single runs of the same cell
  have been measured at 15 / 51 / 65 LLM calls.

## Columns worth reading carefully

* `cost_usd` is **derived** from tokens at one fixed published price table
  (`$0.15 / $0.03 / $0.50` per 1M for input / cached read / output), not taken
  from the provider. Two measured reasons: the account's two wallets bill
  identical tokens exactly 2x apart (269 rows checked, median ratio 2.0000),
  and the custom-endpoint path reports `cost = 0` while returning real tokens.
  `provider_cost_usd` in the raw JSONL keeps the provider's own figure for audit.
* `cache_read_tokens` is separate from `input_tokens` on purpose - the central
  claim under test is that they are different currencies.
* `prompt_peak_tokens` is the largest single prompt the model saw, not a sum.
* `stop_reason` distinguishes a turn-budget stop from a timeout; 200-turn runs
  are budget stops, and they occur in the control too.
* `endpoint` (raw JSONL) records which wallet served the run, so a per-wallet
  effect can be tested rather than assumed absent.

## Exclusions, and why they are not cherry-picking

**187 failed attempts.** Runs where the verifier returned nothing. This is a
count of *attempts*, not holes in the matrix: 149 of those cells were re-queued
by RESUME and closed later with a real verdict, and they appear in the dataset
with that verdict. The residue is dominated by the two unrunnable qemu tasks
(36 attempts) and by cells where the plugin's trace never appeared. In the clean
orchestrator era the residue is symmetric across arms (2/2/2/2), so it does not
favour any condition.

**26 quarantined.** Runs whose turns were partly rate-limited while the run was
being measured at a parallelism above the provider's ceiling. The exclusion rule
was fixed before the counts were seen: `clean` = zero errored turns,
`nominal` = at most two and under 5%, everything else `degraded` and excluded.
This matters because keeping them changed the headline result - the paired
comparison for `tail0` moved from p=7.9e-08 to p=9.2e-02 once they were removed
(`log/RESULT-signal-was-contamination.md`). The contamination was one-directional
by construction: the control had already finished in clean conditions, so
saturation only ever cost the state-block arms turns, and the verifier's honest
zero on a starved run read as the method failing.

**2 collapsed duplicates.** When an orchestrator restart ran one cell twice, the
builder keeps the **earliest launch** - a rule fixed before any verdict was read,
so a rerun cannot promote itself into the sample by winning. Enforced in
`tools/build_canonical_dataset.py` and tested in `tests/test_dataset_dedupe.py`.

## Results

### Solve rate

| condition | solved / runs | rate | 95% CI |
|---|---|---|---|
| baseline | 160 / 261 | 0.613 | [0.553, 0.670] |
| tail0 | 91 / 261 | 0.349 | [0.293, 0.408] |
| tail2 | 118 / 261 | 0.452 | [0.393, 0.513] |
| tail6 | 154 / 261 | 0.590 | [0.529, 0.648] |

### Paired against the control (exact McNemar)

| condition | pairs | control only | condition only | both | p |
|---|---|---|---|---|---|
| tail0 | 261 | 82 | 13 | 78 | 2.1e-13 |
| tail2 | 261 | 58 | 16 | 102 | 9.7e-07 |
| tail6 | 261 | 29 | 23 | 131 | 0.49 |

The method as published (`tail0`) loses 82 tasks and wins 13. The damage falls
monotonically as verbatim history is restored, and at six turns the difference
is indistinguishable from noise. What the state block costs in capability is
paid back by the history it replaces, not by the state block itself.

### The cost of memory, on pairs where both arms solved

Ratios are per-pair medians, so a single expensive task cannot set the number.

| condition | pairs | cost | prompt peak | output tokens | cache reads |
|---|---|---|---|---|---|
| tail0 | 78 | **2.57x** | **0.47x** | 4.55x | 0.89x |
| tail2 | 102 | 1.39x | 0.60x | 2.08x | 0.40x |
| tail6 | 131 | 1.15x | 0.81x | 1.36x | 0.21x |

This is the result that has survived every check. At equal outcome, `tail0`
carries **half the prompt** and costs **two and a half times as much**. The
mechanism is in the same row: rewriting the state block every turn bills those
tokens at the output tariff (4.55x) and destroys the prefix the cache would
otherwise serve. A token-count reduction is not a cost reduction.

### Horizon

Tasks split at the control's median turn count (11 turns): 45 short, 42 long.

| condition | horizon | control only | condition only | p |
|---|---|---|---|---|
| tail0 | short | 28 | 5 | 6.6e-05 |
| tail0 | long | 54 | 8 | 1.7e-09 |
| tail2 | short | 23 | 8 | 1.1e-02 |
| tail2 | long | 35 | 8 | 4.2e-05 |
| tail6 | short | 11 | 10 | 1.00 |
| tail6 | long | 18 | 13 | 0.47 |

The loss **grows** on the long horizon rather than amortising, which is the
opposite of what a memory mechanism is supposed to buy.

### Totals

| condition | cost | turns | input | cache reads | output |
|---|---|---|---|---|---|
| baseline | $17.85 | 6504 | 18.7M | 352.2M | 9.0M |
| tail0 | $14.83 | 16072 | 27.3M | 25.9M | 19.9M |
| tail2 | $12.88 | 10250 | 27.6M | 15.9M | 16.5M |
| tail6 | $11.83 | 4725 | 38.9M | 6.2M | 11.6M |

Whole series: **$57.39**, 37551 turns.

Read the totals with care. Per-condition sums are **not** a fair comparison,
because a failing run stops early and therefore costs less; that is why every
cost claim above is made on pairs where both arms solved the task. The control's
cache reads (352M against tail6's 6M) show the same mechanism from the other
side: an append-only history is almost entirely cache-served, a rewritten state
block is not.

## Reproducing

`tools/build_canonical_dataset.py <out.csv> <raw.jsonl>:terminal-bench-2.0`
rebuilds the CSV from the raw file. Appending later trials has been shown not to
disturb rows already reported: rebuilding from trial 1 alone and then from all
trials leaves every earlier measurement byte-identical, only `source_file`
differs (`tests/test_append_safety.py`).
