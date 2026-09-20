# SKILL.state (arXiv:2608.26263v3) — Full Quantitative & Methodological Extraction

Source: `/opt/data/cache/web/arxiv.org-cd2905023f.md` (full text, read directly — no network fetch needed). Paper: Badhe, Tiwari, Chung (Google LLC / Purdue), "SKILL.state: Scalable Long-Horizon Agent Skills," arXiv:2608.26263v3, 02 Sep 2026.

---

## 1. ALL RESULTS TABLES (verbatim numbers)

### Table 1 (§4.3, embedded before §5) — "Warehouse Management Long-Horizon Scaling using Gemini-3-Flash." Mean ± SD across 5 seeds.

| Horizon (T) | Runtime | Score (Accuracy) | Avg Prompt (Chars) | Total Tokens |
|---|---|---|---|---|
| 10 | Prompt (ReAct) | 0.90 ±0.02 | 3,249 ±94 | 9,438 ±371 |
| 10 | Memory (Summary) | 1.00 ±0.00 | 3,300 ±123 | 9,972 ±204 |
| 10 | Stateful (LangGraph) | 1.00 ±0.00 | 3,430 ±42 | 10,337 ±299 |
| 10 | SKILL.state | 1.00 ±0.00 | 1,775 ±74 | 5,870 ±131 |
| 25 | Prompt (ReAct) | 0.92 ±0.02 | 6,052 ±192 | 42,689 ±2,238 |
| 25 | Memory (Summary) | 0.99 ±0.00 | 6,357 ±203 | 43,067 ±1,948 |
| 25 | Stateful (LangGraph) | 1.00 ±0.00 | 5,858 ±301 | 41,238 ±3,196 |
| 25 | SKILL.state | 1.00 ±0.00 | 1,736 ±49 | 14,714 ±564 |
| 50 | Prompt (ReAct) | 0.88 ±0.04 | 11,931 ±346 | 171,658 ±6,978 |
| 50 | Memory (Summary) | 0.93 ±0.03 | 7,582 ±283 | 131,455 ±6,841 |
| 50 | Stateful (LangGraph) | 0.94 ±0.00 | 11,594 ±438 | 170,992 ±7,918 |
| 50 | SKILL.state | 0.96 ±0.01 | 1,773 ±53 | 30,151 ±1,231 |
| 100 | Prompt (ReAct) | 0.84 ±0.07 | 36,362 ±1,304 | 1,245,413 ±53,241 |
| 100 | Memory (Summary) | 0.87 ±0.05 | 29,607 ±978 | 1,082,154 ±83,212 |
| 100 | Stateful (LangGraph) | 0.91 ±0.02 | 31,354 ±831 | 1,062,387 ±53,839 |
| 100 | SKILL.state | 0.94 ±0.01 | 1,905 ±93 | 65,408 ±5,431 |
| 200 | Prompt (ReAct) | 0.74 ±0.14 | 48,007 ±2,092 | 2,608,755 ±102,415 |
| 200 | Memory (Summary) | 0.84 ±0.09 | 84,364 ±3,446 | 6,175,509 ±294,089 |
| 200 | Stateful (LangGraph) | 0.88 ±0.03 | 72,305 ±3,096 | 5,041,164 ±346,925 |
| 200 | SKILL.state | 0.94 ±0.02 | 1,811 ±184 | 122,384 ±4,522 |

### Table 2 (§5.3) — "Warehouse Noise Robustness (T=50, Gemini-3-Flash)"

| Noise Level | Runtime | Score |
|---|---|---|
| 5 Events (Low) | Prompt | 0.68 |
| 5 Events (Low) | Memory | 1.00 |
| 5 Events (Low) | Stateful | 1.00 |
| 5 Events (Low) | SKILL.state | 1.00 |
| 20 Events (Medium) | Prompt | 0.61 |
| 20 Events (Medium) | Memory | 1.00 |
| 20 Events (Medium) | Stateful | 0.98 |
| 20 Events (Medium) | SKILL.state | 0.97 |
| 50 Events (High) | Prompt | 0.53 |
| 50 Events (High) | Memory | 0.96 |
| 50 Events (High) | Stateful | 0.98 |
| 50 Events (High) | SKILL.state | 0.98 |

### Table 3 (§5.4) — "Warehouse State Recovery (Gemini-3-Flash)"

| Scenario | Runtime | Success | Recovery Steps |
|---|---|---|---|
| A: Secret Audit | Prompt / Memory / Stateful | Yes | 5–8 |
| A: Secret Audit | SKILL.state | Yes | 0 |
| B: Secret Barcode | Prompt / Memory / Stateful | Yes | 6–8 |
| B: Secret Barcode | SKILL.state | Yes | 0 |
| C: Secret Move | Prompt / Memory / Stateful | Yes | 5–8 |
| C: Secret Move | SKILL.state | Yes | 0 |
| D: Canceled Order | All Runtimes | No | N/A |

### Table 4 (§5.5) — "Evaluation on Public Interactive Benchmarks using Gemini-3-Flash"

| Runtime | InterCode CTF (100 Tasks) Pass@1 | Prompt | Tokens | τ-Bench Retail Pass Rate | Prompt | Tokens | τ-Bench Airline Pass Rate | Prompt | Tokens |
|---|---|---|---|---|---|---|---|---|---|
| Prompt (ReAct) | 43.2% | 1,909 | 977k | 48.2% | 2,819 | 4.48M | 21.8% | 5,100 | 4.85M |
| Memory (Summary) | 46.4% | 1,797 | 1.03M | 29.9% | 2,737 | 4.24M | 23.6% | 4,700 | 4.65M |
| Stateful (LangGraph) | 41.8% | 1,946 | 1.13M | 51.7% | 3,065 | 3.92M | 28.1% | 5,400 | 5.28M |
| SKILL.state | 54.2% | 813 | 387k | 58.3% | 3,325 | 3.47M | 32.4% | 2,800 | 2.88M |

Narrative deltas stated in text (§5.5): InterCode CTF pass@1 "+7.8 points over the strongest baseline and +12.4 points over Stateful"; "cutting total tokens by 60.4% vs. ReAct and 65.9% vs. Stateful." τ-Bench Airline: "saving 40.5% tokens vs. ReAct and 45.4% vs. Stateful." τ-Bench Airline baseline prompts described as peaking "above 11,000 tokens/step" while SKILL.state is "∼2,800 tokens/step" (NOTE: this ∼2,800 figure conflicts with the table's "2,800" prompt column, apparently consistent, but the peak-11,000 figure for baselines is NOT itself in the table — it's a qualitative claim only, UNKNOWN which baseline/table cell it refers to exactly).

### Table 5 (§5.6) — "Budget-Matched Controls on Warehouse (T=100, Gemini-3-Flash, Budget ∼1,800 tokens)"

| Runtime / Configuration | Score | Avg Prompt | Total Tokens |
|---|---|---|---|
| Full ReAct (Unbounded) | 0.84 | 36,362 | 1,245,413 |
| Truncated (Sliding Window) | 0.18 | 1,800 | 62,100 |
| Summary-capped | 0.52 | 1,840 | 63,400 |
| ReAct + LLMLingua | 0.22 | 1,810 | 62,350 |
| SKILL.state (Structured) | 0.94 | 1,905 | 65,408 |

### Error taxonomy (§5.7) — "Error Taxonomy for Open-Weight Models" (Gemma-4-31B at T=100, score 0.42; not a table but exact percentages)

| Error Mode | Share of Errors |
|---|---|
| Premature State Overwrite / Deletion | 68% |
| Schema Comprehension / Type Coercion | 20% |
| JSON Syntax / Formatting Slips | 12% |

### Table 6 (Appendix D) — "Software Repository Long-Horizon Execution Scaling using Gemini-3-Flash"

| Horizon | Runtime | Score | Avg Prompt Size | Total Tokens Consumed |
|---|---|---|---|---|
| 10 | Prompt | 0.89 ±0.11 | 3,411 ±197 | 11,670 ±841 |
| 10 | Memory | 0.93 ±0.09 | 4,379 ±234 | 15,732 ±562 |
| 10 | Stateful | 1.00 ±0.00 | 4,200 ±321 | 14,120 ±318 |
| 10 | SKILL.state | 1.00 ±0.00 | 2,298 ±134 | 7,608 ±149 |
| 25 | Prompt | 0.84 ±0.05 | 11,754 ±608 | 111,970 ±3,314 |
| 25 | Memory | 0.89 ±0.07 | 9,399 ±317 | 94,629 ±2,839 |
| 25 | Stateful | 0.94 ±0.03 | 14,016 ±586 | 128,702 ±3,863 |
| 25 | SKILL.state | 0.88 ±0.08 | 2,545 ±556 | 21,920 ±431 |
| 50 | Prompt | 0.71 ±0.14 | 23,136 ±911 | 462,118 ±13,764 |
| 50 | Memory | 0.65 ±0.12 | 35,550 ±2,412 | 688,182 ±23,539 |
| 50 | Stateful | 0.74 ±0.08 | 31,166 ±3,231 | 577,027 ±27,293 |
| 50 | SKILL.state | 0.86 ±0.04 | 2,545 ±63 | 45,100 ±894 |
| 100 | Prompt | 0.53 ±0.16 | 46,270 ±1,847 | 1,848,500 ±55,391 |
| 100 | Memory | 0.57 ±0.05 | 71,100 ±5,836 | 2,752,700 ±82,467 |
| 100 | Stateful | 0.63 ±0.10 | 62,330 ±2,488 | 2,308,000 ±35,183 |
| 100 | SKILL.state | 0.78 ±0.08 | 2,545 ±471 | 90,200 ±2,792 |

(Note: T=200 is NOT reported for Software Repository — only T=10,25,50,100.)

### Table 7 (Appendix D) — "Gemma-4-31b-it Warehouse Scaling"

| Horizon | Runtime | Score ± SD | Avg Prompt ± SD | Total Tokens ± SD |
|---|---|---|---|---|
| 10 Steps | Prompt | 0.90 ±3.1% | 3,145 ±242 | 9,092 ±1,231 |
| 10 Steps | Memory | 0.85 ±4.2% | 2,611 ±138 | 7,330 ±838 |
| 10 Steps | Stateful | 0.90 ±2.8% | 3,191 ±149 | 9,144 ±518 |
| 10 Steps | SKILL.state | 0.98 ±1.5% | 2,116 ±212 | 6,814 ±875 |
| 25 Steps | Prompt | 0.64 ±5.4% | 5,720 ±182 | 41,697 ±1,610 |
| 25 Steps | Memory | 0.72 ±4.8% | 3,990 ±362 | 28,933 ±412 |
| 25 Steps | Stateful | 0.76 ±4.1% | 5,714 ±282 | 39,314 ±585 |
| 25 Steps | SKILL.state | 0.84 ±3.6% | 2,080 ±114 | 16,302 ±2,190 |
| 50 Steps | Prompt | 0.31 ±6.2% | 10,809 ±352 | 151,845 ±2,150 |
| 50 Steps | Memory | 0.41 ±5.8% | 7,217 ±316 | 114,113 ±1,620 |
| 50 Steps | Stateful | 0.55 ±5.1% | 11,083 ±262 | 155,164 ±2,210 |
| 50 Steps | SKILL.state | 0.68 ±3.9% | 2,113 ±176 | 33,762 ±1,385 |
| 100 Steps | Prompt | 0.21 ±4.7% | 27,686 ±412 | 923,164 ±12,400 |
| 100 Steps | Memory | 0.24 ±4.2% | 18,537 ±229 | 701,954 ±9,850 |
| 100 Steps | Stateful | 0.42 ±4.5% | 20,210 ±822 | 557,968 ±8,100 |
| 100 Steps | SKILL.state | 0.42 ±4.1% | 2,105 ±216 | 65,480 ±1,258 |

Note the anomaly (present in the paper itself, not a transcription error): at 100 Steps, Stateful and SKILL.state have **identical** score 0.42 ±4.5%/±4.1% for Gemma-4-31B-it — i.e. no SKILL.state advantage at this horizon/model combination.

### Table 8 (Appendix D) — "Qwen 3-8b-it Warehouse Scaling"

| Horizon | Runtime | Score ± SD | Avg Prompt ± SD | Total Tokens ± SD |
|---|---|---|---|---|
| 10 Steps | Prompt | 0.84 ±3.8% | 3,150 ±245 | 9,150 ±1,250 |
| 10 Steps | Memory | 0.80 ±4.5% | 2,640 ±145 | 7,420 ±860 |
| 10 Steps | Stateful | 0.84 ±3.4% | 3,210 ±155 | 9,210 ±540 |
| 10 Steps | SKILL.state | 0.94 ±2.1% | 2,120 ±215 | 6,920 ±890 |
| 25 Steps | Prompt | 0.54 ±6.1% | 5,790 ±195 | 42,450 ±1,680 |
| 25 Steps | Memory | 0.62 ±5.4% | 4,050 ±375 | 29,640 ±440 |
| 25 Steps | Stateful | 0.66 ±4.8% | 5,780 ±295 | 39,950 ±610 |
| 25 Steps | SKILL.state | 0.76 ±4.2% | 2,088 ±120 | 16,680 ±2,240 |
| 50 Steps | Prompt | 0.24 ±6.5% | 10,950 ±365 | 154,200 ±2,280 |
| 50 Steps | Memory | 0.33 ±6.1% | 7,320 ±330 | 116,400 ±1,710 |
| 50 Steps | Stateful | 0.44 ±5.7% | 11,210 ±280 | 158,300 ±2,340 |
| 50 Steps | SKILL.state | 0.58 ±4.5% | 2,118 ±185 | 34,510 ±1,420 |
| 100 Steps | Prompt | 0.15 ±5.1% | 28,150 ±430 | 941,500 ±12,800 |
| 100 Steps | Memory | 0.18 ±4.6% | 18,840 ±245 | 718,200 ±10,200 |
| 100 Steps | Stateful | 0.31 ±4.9% | 20,580 ±850 | 569,400 ±8,450 |
| 100 Steps | SKILL.state | 0.34 ±4.6% | 2,110 ±220 | 66,850 ±1,310 |

### Table 9 (Appendix D) — "Software Repository Experiment 2 (Noise Robustness)"; 50-step horizon, Gemini-3-Flash

| Noise Level | Runtime | Score |
|---|---|---|
| 0 Events (Baseline) | Prompt | 0.76 |
| 0 Events (Baseline) | Memory | 0.85 |
| 0 Events (Baseline) | Stateful | 0.88 |
| 0 Events (Baseline) | SKILL.state | 0.90 |
| 5 Events (Low) | Prompt | 0.62 |
| 5 Events (Low) | Memory | 0.85 |
| 5 Events (Low) | Stateful | 0.86 |
| 5 Events (Low) | SKILL.state | 0.88 |
| 20 Events (Medium) | Prompt | 0.48 |
| 20 Events (Medium) | Memory | 0.83 |
| 20 Events (Medium) | Stateful | 0.85 |
| 20 Events (Medium) | SKILL.state | 0.86 |
| 50 Events (High) | Prompt | 0.11 |
| 50 Events (High) | Memory | 0.74 |
| 50 Events (High) | Stateful | 0.78 |
| 50 Events (High) | SKILL.state | 0.80 |

### Table 10 (Appendix D, §.1) — "Software Repository State Recovery (Env 2, Exp 3)"

| Scenario | Runtime | Success | Recovery Steps |
|---|---|---|---|
| A: Force Push | Prompt | Yes | 12 |
| A: Force Push | Memory | Yes | 8 |
| A: Force Push | Stateful | Yes | 10 |
| A: Force Push | SKILL.state | Yes | 0 |
| B: Flaky CI Test | Prompt | Yes | 14 |
| B: Flaky CI Test | Memory | Yes | 9 |
| B: Flaky CI Test | Stateful | Yes | 11 |
| B: Flaky CI Test | SKILL.state | Yes | 0 |
| C: PR Closed | All Runtimes | No | N/A |

### Table 11 (Appendix D, §.2) — "Extended Budget-Matched Scaling on Warehouse across Horizons (Gemini-3-Flash, Target Budget ∼1,800 tokens, Score ± SD across 5 seeds)"

| Horizon (T) | SKILL.state | Summary-capped | Truncated (Window) | ReAct + LLMLingua | ReAct (Full) |
|---|---|---|---|---|---|
| 10 | 1.00 ±0.00 | 0.92 ±0.03 | 0.90 ±0.04 | 0.88 ±0.04 | 0.90 ±0.02 |
| 25 | 1.00 ±0.00 | 0.76 ±0.04 | 0.62 ±0.05 | 0.60 ±0.05 | 0.92 ±0.02 |
| 50 | 0.96 ±0.01 | 0.64 ±0.05 | 0.35 ±0.06 | 0.38 ±0.06 | 0.88 ±0.04 |
| 100 | 0.94 ±0.01 | 0.52 ±0.05 | 0.18 ±0.05 | 0.22 ±0.05 | 0.84 ±0.07 |

**All tables from the document have been reproduced above (Tables 1–11 inclusive). No table was skipped.**

---

## 2. EXPERIMENTAL SETUP

**Benchmarks/datasets and task counts:**
- **SkillExecBench** (paper's own synthetic benchmark): two environments —
  - Env 1 "Warehouse Management": 500 independent shelves (discrete inventory). No fixed "number of tasks" — horizon T is swept as the independent variable (T ∈ {10, 25, 50, 100, 200} in main text; T ∈ {10,25,50,100} in Appendix D extended budget table). Tasks are procedurally generated with a fixed RNG seed=42 (Algorithm 2), and "5 distinct procedural generator seeds" are used for statistical variance (see below) — it is UNCLEAR/possibly contradictory whether seed=42 is one fixed seed for task structure while 5 different seeds vary something else, or whether "5 seeds" means 5 different generator seeds each producing a different task instance. The paper states both "seed ← 42" in the pseudocode and "5 distinct procedural generator seeds" in §5.1 — this is a point the paper does not fully reconcile; FLAG: ambiguous/underspecified how the 5 seeds relate to the single seed=42 shown in the algorithm.
  - Env 2 "Software Repository": a simulated Git repo (branches, commits, PRs, CI statuses); horizon T ∈ {10,25,50,100} (no T=200 reported for this environment).
- **InterCode CTF** (Yang et al. 2023): 100 Linux bash CTF challenge tasks (reverse engineering, forensics, cryptography, binary exploitation).
- **Sierra τ-Bench** (Yao et al. 2024): two domains, Retail and Airline. Exact task counts for τ-Bench are NOT SPECIFIED in this paper (not stated numerically anywhere in the text; the paper only names the domains).

**Models evaluated (exact identifiers as given in the paper):**
- **Gemini-3-Flash** (proprietary) — used for essentially all main-text tables (1–6, 9–11) and most Appendix D tables.
- **Gemma-4-31B-it** (open-weight) — used in Table 7 and the §5.7 error taxonomy (called "Gemma-4-31B" in §5.7 text and "Gemma-4-31b-it" in Table 7 title — same model, inconsistent capitalization only).
- **Qwen 3-8B-it** (open-weight) — used in Table 8 (paper text calls it "Qwen-3-8B-it" in §5.1 and "Qwen 3-8b-it" in the Table 8 title).
No further version/checkpoint/date identifiers (e.g., no API version strings, no HuggingFace repo IDs) are given for any of the three models. This is UNDERSPECIFIED for reproduction — there is no way to know the exact model snapshot/weights from the paper alone.

**Baselines and exact configuration:**
Primary Runtime Paradigms (§5.1):
1. **Prompt (ReAct-style)** — appends every observation, reasoning trace, and action to a continually growing transcript (Yao et al. 2022). No length limit.
2. **Memory (Summarization-style)** — "Maintains a rolling **3-step** conversational window alongside a periodically updated natural language summary of past interactions." Exact summarization trigger/policy (how often the summary updates, what model summarizes, target length of the summary in the *unconstrained* Memory variant) is NOT SPECIFIED beyond "periodically updated."
3. **Stateful (LangGraph-style)** — "Injects a structured state block into the context window alongside the full rolling conversational transcript" (i.e., state block PLUS unbounded/full history — this is the key distinguishing feature vs. SKILL.state, which discards history).

Budget-Matched and Compression Controls (§5.1, used in Table 5 and Table 11):
4. **Truncated (Sliding Window)** — "Retains only the most recent interaction turns that fit within a fixed token budget." Budget target: ∼1,800 tokens (stated as "∼1,800 characters" in §5.6 text but "Target Budget ∼1,800 tokens" in Table 11 caption — the paper itself is inconsistent between "characters" and "tokens" for this budget figure; FLAG this discrepancy explicitly).
5. **Summary-capped** — "Strictly enforces a hard token ceiling on the natural language summary." No numeric ceiling other than the shared ∼1,800 target budget is given; algorithm for what gets dropped when the cap is hit is NOT SPECIFIED.
6. **ReAct + LLMLingua** (Jiang et al. 2023) — "Uses budget-aware small-model perplexity compression to prune tokens from the full history down to the target budget." No LLMLingua compression ratio, target token count, or which LLMLingua variant (LLMLingua vs LongLLMLingua vs LLMLingua-2) is specified — this is a significant methodological gap for reproduction. FLAG: NOT SPECIFIED — exact compression ratio / config for LLMLingua is absent.

The Appendix A prompt templates give the literal prompt-construction skeletons for Prompt/Memory/Stateful/SKILL.state runtimes (see Section 7 below), but do NOT give templates for the three "Budget-Matched and Compression Controls," so their exact prompt construction is not independently verifiable from Appendix A either.

**Horizon values swept and how horizon is defined/controlled:**
- Main scaling sweep (Table 1, Warehouse): T ∈ {10, 25, 50, 100, 200}.
- Software Repository scaling (Table 6): T ∈ {10, 25, 50, 100} (no 200).
- Gemma/Qwen scaling (Tables 7, 8): T ∈ {10, 25, 50, 100}.
- Noise robustness experiments (Tables 2, 9): horizon fixed at T=50.
- Budget-matched Table 5: single horizon T=100. Extended budget-matched Table 11: T ∈ {10,25,50,100}.
- Horizon T is defined as the number of sequential events/steps the agent must handle, generated by Algorithm 2 (Warehouse Task Generation): "The horizon length dictates the number of sequential events the agent must handle." It is controlled by procedurally generating exactly T events via a seeded RNG, and "seeding the generator... guarantee[s] that all evaluated baseline runtimes experience the exact same sequence of events, ensuring fair comparisons" — i.e., horizon = fixed number of environment-generated events, held identical across all runtimes for a given seed.

**Repetitions/seeds and variance reporting:**
- "All synthetic experiments are evaluated across **5 distinct procedural generator seeds**. Results are reported as **mean ± sample standard deviation**." (§5.1)
- Statistical significance claim: "Differences between SKILL.state and baselines at extended horizons (T≥50) are statistically significant (**paired t-test, p<0.01**)." No specific p-values per comparison are given, no test statistics, no indication of which exact pairs of runtimes/horizons this significance claim covers beyond the blanket "T≥50" statement, and no correction for multiple comparisons is mentioned. FLAG: this significance claim is asserted, not shown (no per-cell p-values, no supplementary stats table).
- Tables 2, 3, 9, 10 (noise/recovery experiments) report **single point values with no ± SD and no stated number of repetitions** — it is NOT SPECIFIED whether these are single-seed runs or an average without reported variance. This is a clear place where a reproduction may diverge, since the number of trials underlying these numbers is unknown.
- Table 4 (InterCode CTF / τ-Bench) similarly reports single point values (Pass@1 %, Pass Rate %) with **no ± variance, no seed count stated**. Because InterCode CTF and τ-Bench are the two "real-world" benchmarks and not synthetic-generator-seeded, it is UNSPECIFIED whether these figures represent one full pass over the 100 CTF tasks (i.e., n=100 tasks pass@1 average) or an average of multiple independent runs. Given "100 Tasks" is stated for InterCode CTF, the 43.2%/46.4%/41.8%/54.2% Pass@1 numbers are presumably a single fraction over the 100 tasks (i.e., ~43/46/42/54 tasks solved) — but the paper never explicitly confirms this is exactly one evaluation pass with no repeats.

**Decoding settings:** "Decoding is controlled at temperature 0.0 and top-p 1.0 across all runs to ensure deterministic reproducibility." (This nominally conflicts with running "5 distinct procedural generator seeds" for variance — if decoding is deterministic (temp=0), the variance across the 5 seeds must come entirely from the different generated task instances/event sequences, not from stochastic decoding. This is a real but plausible explanation, not a contradiction, but worth flagging: at temperature 0 the seed-to-seed variance reflects difficulty variation across generated episodes, not sampling noise.)

**Budget-matching methodology (§5.6, Experiment 5):** The stated purpose is "to determine whether SKILL.state's performance gains stem merely from shorter prompts or from structured state representation." The three budget-matched/compression controls (Truncated, Summary-capped, ReAct+LLMLingua) are each "pinned to the token budget of SKILL.state (∼1,800 characters)" [note again the characters/tokens inconsistency flagged above] at T=100 on Warehouse with Gemini-3-Flash. What is held equal: the **average prompt size** (∼1,800 tokens/characters) across all four arms (see Table 5's "Avg Prompt" column: 1,800 / 1,840 / 1,810 / 1,905 — all approximately matched). What is explicitly NOT held equal or specified: the underlying model, decoding params, and action space are presumably identical (same as other experiments) but this is not explicitly restated for Experiment 5. The exact mechanism used to hit the ∼1,800 budget for each compression method (e.g., iterative pruning algorithm, stopping criterion) is NOT SPECIFIED beyond the one-line descriptions in §5.1.

---

## 3. STATE SCHEMAS

The paper's ONLY explicit, verbatim, named-field schema is for InterCode CTF:

> "Schemas are authored once per domain rather than per task; for example, across all 100 diverse challenge instances in the InterCode CTF benchmark, the agent reuses a single static 5-field schema (**discovered_flags, tested_hypotheses, active_files, working_dir, cmd_summary**)." (§3.1)

For **SkillExecBench Warehouse (Env 1)**, no named JSON-schema field list is given; instead the paper describes the state as: "A discrete inventory mapping of 500 independent shelves (e.g., shelf_0 through shelf_499), where each shelf holds exactly one item string identifier or is null." (Appendix B.1). The Appendix B.3 example trajectory shows a state_patch touching an `"inventory"` key with sub-keys like `"shelf_42": null`, implying the schema is effectively `{"inventory": {shelf_id: item_id_or_null, ...}}`, but this exact top-level schema (e.g., whether there are other top-level keys beyond `inventory`) is **NOT fully specified/quoted** as a schema definition — it is inferred only from the one example trajectory, not stated as a formal schema list.

For **SkillExecBench Software Repository (Env 2)**, similarly no named field list; description only: "A simulated Git repository tracking branch histories, file contents, active Pull Requests (PRs), and Continuous Integration (CI) test statuses." (Appendix B.1). No verbatim schema/field names are given for this environment at all.

For **Sierra τ-Bench** (Retail/Airline), **no schema is given anywhere in the paper** — the paper does not describe or quote any state schema for τ-Bench.

**Does the paper explain HOW schemas were designed/chosen?** No. The paper states only that "Schemas are authored once per domain rather than per task" (§3.1) — a claim about the *authoring cadence* (once per domain, reused across tasks), not a method for *how* the schema fields were chosen/derived. There is no ablation, no discussion of schema-design principles, no sensitivity analysis of schema completeness, and no discussion of who/what process produced the specific field names. **The schemas are presented as given / a priori artifacts of the runtime implementation, with no justification of design process.** This is a significant methodological gap for reproduction: a reproducer must invent their own schema for any domain not explicitly named (InterCode CTF is the only domain with a quoted field list), which is a legitimate and expected source of divergence.

---

## 4. METRIC DEFINITIONS (§4.3, verbatim)

- **Task Accuracy / Success Rate:**
  - **SkillExecBench:** "accuracy is measured continuously as the ratio of valid, correct actions matching the ground-truth deterministic simulation (**Score = Successful Actions / Total Actionable Events**)." (Formula given explicitly.) Also restated in Appendix B.1 for Warehouse: "The ratio of successfully executed valid actions matching the ground-truth deterministic simulation (Score = Successful Actions / Total Actionable Events)." For Software Repository (Appendix B.1): "The percentage of correctly resolved feature requests merged into master without breaking CI checks" (a differently-worded success criterion for Env 2, not literally the same formula as Env 1, though presumably analogous).
  - **InterCode CTF:** "success is binary pass@1 (exact match on the binary-verified flag)."
  - **τ-Bench:** "success is scored by the official programmatic evaluator, which verifies that the final database state satisfies user intent without policy violations." (No formula given; delegated to the external τ-Bench evaluator, not defined within this paper.)
- **Average Prompt Size:** "The mean string character length per LLM invocation." (Explicitly *character* length, not token count — note that Table 1's column header is "Avg Prompt (Chars)" consistent with this, but Table 11's caption says "Target Budget ∼1,800 tokens" for the same quantity — an internal inconsistency between "characters" as defined in the metric section and "tokens" as used in some table captions/text. FLAG this unit inconsistency explicitly for reproduction — the paper is not self-consistent about whether prompt-size budgets are in characters or tokens.)
- **Total Token Cost:** "The cumulative token burn across the entire execution horizon." No formula beyond this one-sentence definition; no specification of tokenizer used, whether input+output tokens are both counted, or whether it's per-model tokenization (Gemini vs Gemma vs Qwen tokenizers presumably differ, and the paper doesn't address how token counts are made comparable across models in Tables 6/7/8).
- **Recovery Steps** (Experiment 3 / Tables 3, 10): Defined only narratively — "history-based baselines hallucinate for 5 to 8 consecutive turns because obsolete facts in their prompt history overpower contradictory new observations" — i.e., recovery steps = number of consecutive turns before the agent's behavior reflects the corrected/updated true state after an external state-drift event. No formal formula given.
- **Error Taxonomy percentages** (§5.7): defined as proportions of "failure logs" categorized into three mutually exclusive error modes for Gemma-4-31B at T=100; no formula, and the denominator (total number of failed steps/episodes analyzed) is NOT SPECIFIED numerically.

---

## 5. TOKEN COST / ECONOMICS — CACHING AND MONETARY COST TREATMENT

A targeted search of the full paper text for "cache", "caching", "prefix cache", "cache hit", "$", "dollar", "monetary", "price", "billing", "USD" returns **zero matches**. The paper contains **no mention whatsoever** of prompt caching, prefix caching, cache hits, or any real monetary/dollar cost.

All cost-related claims in the paper are strictly in terms of **logical token counts** and **character-length prompt sizes**, as defined in §4.3:
- "Average Prompt Size: The mean string character length per LLM invocation."
- "Total Token Cost: The cumulative token burn across the entire execution horizon."

Every quantitative claim about "token reduction," "cost," "savings," etc. throughout the Results sections (e.g., "a 16.2× token reduction" at T=100 in §5.2; "cutting total tokens by 60.4% vs. ReAct" in §5.5; "saving 40.5% tokens vs. ReAct and 45.4% vs. Stateful" in §5.5) is computed purely from these raw cumulative-token/character counts, with **no adjustment for, or even acknowledgment of, provider-side prefix/prompt caching, which in practice would substantially discount the *marginal* cost of repeatedly re-sending an ever-growing but highly-overlapping prompt prefix** (as in the ReAct/Stateful baselines, which append to a shared growing prefix that a caching-aware provider would bill much cheaper on repeat turns than the raw token count implies). The paper's entire economic argument is a **logical/nominal token-count argument, not a real dollar-cost argument**, and it never engages with the caching question at all.

**This is directly relevant to the reproduction's finding:** since the paper never measures or discusses cache-hit-adjusted or monetary cost, a reproduction that finds SKILL.state more expensive than a full-history baseline *under real provider billing with prefix caching* is not contradicting any explicit claim in this paper — the paper's claims are scoped exclusively to raw/logical token counts and character-length prompt sizes, and it makes no representation about real-money cost or cache-adjusted cost. Any comparison to "the paper's economics claims" must be understood as a comparison to *logical token counts only*; the paper is silent, not merely brief, on caching and monetary cost.

---

## 6. LIMITATIONS SECTION (§7, quoted in full)

> "SKILL.state assumes that the execution state can be made a *sufficient statistic* for future execution: that everything in the past bearing on future actions can be projected into the structured state as soon as it becomes known. Where this holds, discarding intermediate reasoning and conversational history is lossless. However, this assumption fails in three distinct settings: (1) when no fixed schema is known in advance and the relevant state structure must be discovered dynamically during execution; (2) when a correct state update depends on an earlier observation whose relevance was not recognized when first observed, and was therefore never committed to state; and (3) when the task objective is defined over the historical trajectory itself (e.g., auditing, debugging provenance, or explaining past actions), where interaction history is the target output rather than operational overhead.
>
> Our current implementation focuses on single-agent procedural execution. While the explicit state abstraction extends naturally to multi-agent systems—where a shared execution state acts as the central coordination substrate instead of exchanging quadratic conversational transcripts—multi-agent environments introduce concurrent writes, requiring deterministic conflict-resolution semantics in the merge operator ⊕ that our single-agent setting does not exercise.
>
> Finally, SKILL.state relies on the language model to propose valid structured state patches. Because schema ownership and validation reside in the deterministic runtime rather than the model, malformed outputs cannot corrupt persistent state Σt; an invalid patch triggers a rollback-retry cycle. For smaller open-weight models, integrating grammar-constrained decoding can eliminate syntactic formatting errors, allowing the model to focus entirely on semantic state transitions."

(This is the complete Section 7; no further limitations paragraphs exist in the paper.)

---

## 7. APPENDIX A (Runtime Prompts) and APPENDIX B (Environment Descriptions)

### Appendix A — Runtime Prompts (summary + verbatim key content)

States: "This appendix provides the exact system prompts used by the four evaluated runtimes. To ensure reproducibility, all prompts are presented exactly as they were dynamically constructed and formatted in the benchmark execution loop." Four templates given:

- **A.1 Prompt Runtime (ReAct-style):** Template appends `Instructions: {skill.instructions}`, then a growing `History:` block with `Observation:`/`Reasoning & Action:` pairs for every past step ("[...Appends all previous observations and actions...]"), then `Latest Observation: {observation}`, then asks the model to "Generate your next reasoning and action (format 'Action: <cmd>')."
- **A.2 Memory-Augmented Runtime:** `Instructions:` + `Summarized History: {summary_string_of_past_steps}` + `Recent History:` containing the **3 most recent** observation/response turns ("[...Appends the 3 most recent turns...]") + `Latest Observation:` + same "Generate your next reasoning and action" instruction.
- **A.3 Stateful Runtime (LangGraph-style):** `Instructions:` + `Current State: {json.dumps(state, indent=2)}` + a full growing `History:` of all previous observation/response pairs ("[...Appends all previous observations and actions...]") + `Latest Observation:` + instruction: "Update the state if necessary, provide reasoning, and output 'Action: <cmd>'. To update state, use the format: StateUpdate: {"key": "value"}" — i.e., reasoning/action and state update are requested in the **same single model output**, but the state update is a free-form trailing `StateUpdate: {...}` block appended after the reasoning/action text, distinct from SKILL.state's single fenced JSON block.
- **A.4 SKILL.state Runtime:** `Instructions:` + `Skill Execution State:` (JSON, compact separators) + `Latest Observation: {observation}` + instruction: "Provide your response with: 1. Step-by-step reasoning (will be discarded after execution) 2. A JSON block fenced with ```json ... ``` containing both your State Patch and your Action. The JSON block MUST have exactly these two keys: { "state_patch": { <dict: your state updates, set keys to null to delete> }, "action": "<string: the exact command you want to execute>" }"

**Critical detail for the reproduction question (single vs. separate emission):** In SKILL.state, the state update (`state_patch`) and the action are explicitly emitted **together, in a single model output**, as one fenced JSON block containing both `state_patch` and `action` keys — confirmed by both the A.4 template ("A JSON block ... containing both your State Patch and your Action... MUST have exactly these two keys: state_patch, action") and by Eq. (3) in the main text: "the language model generates: (R_t, ΔΣ_t, a_t)" — i.e., reasoning, state delta, and action are all produced in one generation call per step, not as separate model invocations. The Appendix B.3 example trajectory confirms this concretely: step 3 ("State Update and Action Generation (LLM → Runtime)") shows a single JSON object `{"state_patch": {"inventory": {"shelf_42": null}}, "action": "Ship item_12 shelf_42"}` — one combined output. The Stateful (LangGraph-style) baseline similarly requests both in one output but with a different, less structured format (trailing `StateUpdate: {...}` text block rather than a single strict two-key JSON schema).

The appendix closes with: "Note: The skill.instructions placeholder dynamically injects the task-specific system prompt (e.g., the agent's persona, the available action space, and the environment rules). This ensures that across all runtime evaluations, the agent receives the exact same baseline instructions, isolating context management as the only independent variable."

### Appendix B — SkillExecBench Implementation Details (summary + verbatim key content)

**B.1 Environment Design:**

*Environment 1: Warehouse Management*
- State Representation: "A discrete inventory mapping of 500 independent shelves (e.g., shelf_0 through shelf_499), where each shelf holds exactly one item string identifier or is null."
- Action Space: `Store <item_id> <empty_shelf_id>`, `Ship <item_id> <shelf_id>`, `Move <item_id> <old_shelf_id> <new_shelf_id>`, `Wait`.
- Observation Format: "Textual alerts triggered by system events, including: Shipment arrived containing [item], Customer ordered [item], and Maintenance required on [shelf]."
- Transition Rules: "If an agent calls Store, the environment validates the shelf is empty before placing the item. If Ship is called, the item is destroyed. Invalid actions (e.g., storing an item on an occupied shelf) return a local error observation and reject the state transition."
- Success Criterion: "The ratio of successfully executed valid actions matching the ground-truth deterministic simulation (Score = Successful Actions / Total Actionable Events)."

*Environment 2: Software Repository*
- State Representation: "A simulated Git repository tracking branch histories, file contents, active Pull Requests (PRs), and Continuous Integration (CI) test statuses."
- Action Space: `Commit(branch, file)`, `CreatePR(branch)`, `Merge(pr_id)`, `FixCI(branch)`, `Wait`.
- Observation Format: "CI/CD webhook notifications (e.g., CI Pipeline Failed for PR #3), code review comments, and issue assignments."
- Transition Rules: "Pushing a commit triggers a background CI evaluation transition. Merging a PR successfully transitions the master branch state and deletes the feature branch."
- Success Criterion: "The percentage of correctly resolved feature requests merged into master without breaking CI checks."

**B.2 Task Generation:** "Tasks are procedurally generated using a deterministic random number generator. By seeding the generator, we guarantee that all evaluated baseline runtimes experience the exact same sequence of events, ensuring fair comparisons. The horizon length dictates the number of sequential events the agent must handle." Algorithm 2 (Warehouse Task Generation Pseudo-code) is given explicitly: `seed ← 42`; `rng ← Random(seed)`; initialize all 500 shelves to Null; loop `i=1` to `Horizon`: find empty/occupied shelves, build a `possible_events` list (`Receive` always available; `Order`, `Maintenance` added only if some shelf is occupied), sample `event_type ← rng.choice(possible_events)`, construct and append the observation, update ground truth accordingly.

**B.3 Example Episode Trajectory** (single-turn, SKILL.state runtime, Warehouse): shows the exact 4-part sequence — (1) Observation: "Customer ordered item_12." → (2) internal reasoning (discarded) locating item_12 on shelf_42 → (3) combined model output `{"state_patch": {"inventory": {"shelf_42": null}}, "action": "Ship item_12 shelf_42"}` → (4) next observation: "Success: Shipped item_12 from shelf_42." This confirms the single combined-output mechanism described above.

**Appendix C (Noise Construction, Experiment 2) — summary:** Noise is restricted to "Condition 1: Irrelevant Context" only (the paper explicitly notes it "exclusively focus[es] on Condition 1," implying other unstudied noise conditions were conceived but not evaluated — UNSPECIFIED what those other conditions would have been). Three defining properties of injected noise: (1) Randomly Generated (battery %, temperatures, server IDs, CPU loads sampled uniformly at random each step); (2) Strictly Irrelevant (no bearing on task); (3) Non-State-Altering (never changes ground-truth world state; purely appended under a `--- BACKGROUND TELEMETRY ---` header). Warehouse distractor categories: Robot Telemetry Logs, Environmental Sensor Logs, Camera OCR/Vision Logs (each with a verbatim example string given). Software Repository distractor: Syslog Telemetry (verbatim example given: `[Syslog] Server-42 CPU load: 88%, RAM usage: 71%` etc.), plus a full example of a "Corrupted Observation" showing the `--- BACKGROUND TELEMETRY ---` header format appended after the real CI-failure observation.

**Appendix D (Additional Results) — summary:** Contains Tables 6–11 (Software Repository scaling, Gemma/Qwen Warehouse scaling, Software Repository noise/recovery experiments, and extended budget-matched scaling), all reproduced in Section 1 of this report above. No further prose beyond brief table-introducing sentences already quoted/paraphrased above.

---

## 8. EXPLICIT LIST OF VAGUE/UNDERSPECIFIED METHODOLOGY POINTS (flagged for reproduction divergence)

1. Relationship between the single fixed seed (42, in Algorithm 2 pseudocode) and the "5 distinct procedural generator seeds" used for variance — not reconciled.
2. Units inconsistency: "Avg Prompt" is defined as character length (§4.3) but budget targets are stated in both "characters" (§5.6 text) and "tokens" (Table 11 caption) — paper is internally inconsistent.
3. No LLMLingua compression ratio, target-length parameter, or LLMLingua variant specified.
4. No exact algorithm/stopping rule for how Truncated (Sliding Window) or Summary-capped controls are made to hit the ∼1,800 budget.
5. No exact task count given for τ-Bench Retail/Airline (only InterCode CTF's 100 is stated).
6. No repetition count or variance reported for InterCode CTF, τ-Bench, or the two "Noise Robustness"/"State Recovery" experiment tables (2, 3, 9, 10) — only single point values.
7. No p-values, test statistics, or full significance table beyond the single blanket claim "paired t-test, p<0.01" for "T≥50" differences.
8. No formal/complete state schema given for Warehouse or Software Repository environments (only inferred from one example trajectory for Warehouse; none at all for Software Repository or τ-Bench).
9. No explanation of HOW any schema (including the one explicit InterCode CTF 5-field schema) was designed/chosen — presented as a given artifact, not derived or justified.
10. No tokenizer specification for "Total Token Cost," and no discussion of how token counts are made comparable across the three different model families (Gemini, Gemma, Qwen) which almost certainly use different tokenizers.
11. No model version/snapshot/date identifiers beyond the bare names "Gemini-3-Flash," "Gemma-4-31B-it," "Qwen-3-8B-it."
12. No engagement anywhere with prompt/prefix caching or real monetary cost — all cost claims are logical-token/character-count claims only (Section 5 above).
13. Denominator for the §5.7 error-taxonomy percentages (total number of failed steps analyzed) is not given.
14. Table 7 anomaly: SKILL.state and Stateful baseline achieve identical score (0.42) for Gemma-4-31B-it at Horizon=100 Steps — the paper's narrative claims of consistent SKILL.state superiority do not strictly hold at this cell, and the paper does not comment on this exception.

---

## Files created
None — this is a research/extraction task; the report above is the complete deliverable, generated directly from the cached full-text paper with no fabricated or inferred numbers. All figures are transcribed verbatim from the source; every place where the paper itself is vague, inconsistent, or silent (especially on caching/monetary cost) is flagged explicitly rather than guessed.