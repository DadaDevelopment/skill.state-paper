# Research-log evidence map

Author-facing audit, not manuscript prose. Prepared from the complete extraction of `наброски по статье-4.docx`, `build/research/notes-4.md`, lines 1–3707. The source document is unchanged. Line references below refer to that extraction. The entire initial proposal and chronological log were read; the two bilingual manuscript generations were separately checked for additions, revisions, and unsupported repetitions.

Purpose: remove laboratory chronology from the paper **without removing experimental knowledge**. A paragraph in a draft is a lead, not an additional independent observation. “Measured” below describes the source's status; admission to a new numerical table additionally requires available data and a reproducible calculation. Neither missing raw data nor a superseded statistic makes the scientific question disappear.

## Priority decisions

1. Restore the complete history-window sweep: state + `k=0,2,6,12,∞`, alongside a separate no-state full-history control. The original proposal explicitly introduced the sweep to avoid an arbitrary choice of six messages. The infinity condition still maintains state and is not the control.
2. Put quality, turns, monetary cost, and efficiency in one repeatable table panel; put prompt/input/cache/output and cache-hit in a second panel with identical rows. Use the same definitions and order for window, runtime-composition, protocol, and horizon comparisons. Do not infer cache-hit from separately aggregated token medians.
3. Investigate a **local diminishing-return hypothesis**, not an equivalence claim: pilot repetition medians reach 1.00 at six and remain there for larger windows, whereas prompt size continues growing. Check all three repeats and direct six-versus-twelve/infinity contrasts. The screenshot uses task-level success counts during a multi-repeat experiment, without a sufficiently explicit repeat-aggregation rule; it cannot by itself establish equal per-episode solve rates.
4. Use control-derived task horizon, fixed across all treatments; show quality and economics together within each cohort. Do not define task length from the treatment's own trajectory. A long failed loop is an outcome, not an independent horizon manipulation.
5. Preserve the engineering argument: runtime records and recent dialogue repair different omissions. The former avoids asking the model to reproduce observable facts; the latter retains the local interaction sequence. Neither is a demonstrated replacement for all history, nor proof that adaptive switching or retrieval works.
6. Retain original-paper repricing only as an explicitly assumed **discounted-token sensitivity proxy**, not a reconstructed invoice. The log multipliers can be reconstructed exactly, but they apply an input-cache discount to undifferentiated total tokens.

## Status vocabulary and source inventory

- **Measured / reanalyse:** the log describes a completed measurement; prefer recomputation from admitted rows.
- **Reported / raw verification missing:** a measurement is described, but the necessary raw sessions or generator are not part of the inspected release. It cannot acquire a stronger status by appearing in a later draft.
- **Superseded:** a later complete sample or corrected extraction replaces an earlier partial result.
- **Retracted:** the claimed interpretation was explicitly invalidated. Preserve the exclusion decision here, not the incident in the manuscript.
- **Planned:** a proposed experiment, architecture, or hypothesis; not an observed improvement.

Available references at the start of this audit:

| Evidence family | Available artifact | Admission boundary |
|---|---|---|
| Broad model-written memory comparison | `data/e1-release/canonical-e1-full.csv`, raw JSONL, `TABLES.txt` | Completed comparison; do not merge with the earlier selected-task window pilot. |
| Final hybrid comparisons | `data/followup-final/arm-summary.csv` and README | Final aggregates, not final per-episode observations; some metrics cannot be recovered from marginal summaries. |
| Runtime composition | `data/v-axis/vaxis-trial1.jsonl`, README | Complete first-repeat variants; some rows overlap the final hybrid comparison, so not independent replication. |
| Complete historical window pilot | `results/TABLES.txt`; log 1533–1583 | Descriptive full-window economic summaries are available. Raw `data/canonical-runs.csv` and original tools are referenced by the reports but were not present in the initial inspected tree. Raw recovery is a separate admission step. Task-level outcomes (solved in any repeat, discordant counts, McNemar p, output per turn) from log 1281-1291 and 1405-1415 are admitted as reported values in `data/pilot-window/log-task-outcomes.csv` and shown in `tab:window-tasks`. |
| Pilot tool repetition | `results/RESULT-redundant-work.md` | Contains full-window descriptive medians and cell-level sign counts. Reported inferential unit needs correction before reuse. |
| Pilot horizon | `results/RESULT-horizon-independence.md`, `HORIZON-REDUNDANCY.txt` | Task-level descriptive correlation; purported detectability threshold is not a power analysis. |
| Per-turn cache example | `results/MECHANISM-fix-git.txt` | One explicit paired usage sequence; descriptive illustration, not population causal identification. |
| Harder-task preview | `results/REDUNDANCY-tb4.txt` | Incomplete, unequal pilot; cannot supply a comparative solve-rate or completed-horizon claim. |
| Original publication | `docs/PAPER-EXTRACTION-full.md`; official arXiv v3 | Verify publication claims against primary source; local extraction is a navigation aid. |

## Initial scientific design: every substantive block

| ID | Source lines | Contribution to recover | Evidence status | Paper destination and qualification |
|---|---|---|---|---|
| D01 | 1–29 | Four concerns: domain schema, early overhead, lost history, missing cache accounting; proposed engineering repairs | Author's research intent | Introduction/discussion as questions. Do not state all four were experimentally established. |
| D02 | 31–76 | Memory decomposition into active history, runtime facts, semantic state, external archive; policy chooses active representation | Planned general model | Method may use the implemented history/runtime/semantic subset. Archive and switching remain future work. |
| D03 | 77–136 | Controlled schema families: generic, remove-field, collapse, noise, capacity, wrong-domain, generated; robustness curve and falsification | Planned broad perturbation study | Discussion/future work. A single task-fit schema comparison is not this robustness curve. |
| D04 | 137–210 | Fixed/adaptive transcript-to-state switching; horizon-dependent crossover; no universal threshold | Planned policy comparison | Discuss as a design implication, not measured adaptive dominance. Static window sweeps do not identify the optimal switch time. |
| D05 | 211–306 | Runtime-derived objective facts versus model-maintained hypotheses; quality and corruption metrics; ledger-only baseline | Partly implemented, partly planned | Explain ownership in Method and composition results; reject guarantees about unmeasured corruption, stale evidence, or ledger-only superiority. |
| D06 | 307–372 | Late-relevance tasks with controlled delay and external retrieval archive | Planned, not measured | Future work; no recovery-rate claim. History kept outside active context is not itself an evaluated retrieval policy. |
| D07 | 373–408 | Cache-aware accounting belongs in every comparison; logical tokens, provider cost, and latency differ | Method requirement; token/cost measurements available | Methods once, shared table contract throughout. Separate normalized prices from paid invoices and do not claim latency when unmeasured. |
| D08 | 409–436 | Broad baseline matrix separates state+full history from no-state transcript, deterministic ledger, retrieval, adaptive policy | Planned matrix, only a subset measured | Explicitly name evaluated conditions. The separate state+full-history row is essential for `k=∞`. |
| D09 | 437–472 | Controlled causal manipulations versus realistic repository tasks; treatment turn count is endogenous | Method principle | Methods + horizon Results. Control-derived horizon is descriptive task stratification, not random assignment of difficulty. |
| D10 | 473–498 | Hierarchy of quality, cost-per-success, active-context scaling, robustness, recovery | Measurement intent | Retain first three where supported; avoid a long flat list of unmeasured metrics. |
| D11 | 499–540 | Four-panel limitation map and one repair mechanism per limitation | Proposed presentation and architecture | Preserve the logical mapping, but do not draw unmeasured schema/retrieval curves. |
| D12 | 541–570 | Explicit guardrails against universal victory, universal threshold, schema elimination, free retrieval | Scope constraints | Discussion/conclusion should state the measured operating trade-offs without inventing a complete repair. |

## Chronological log: complete measurement and design coverage

| ID | Source lines | Factual/design contribution | Status and evidence | Destination / admission decision |
|---|---|---|---|---|
| L01 | 571–590 | Measurement-stage and gate status | Historical workflow | Exclude narrative. Use final data admission rules only. |
| L02 | 591–625 | Pi extension replaces active history; schema-validated separate state-patch tool; stack and smoke contracts | Implemented design, historical version | Methods implementation distinctions; stack details in reproducibility appendix. No import-failure story. |
| L03 | 627–641 | Small fix-git comparison includes turns, prompt, money, cache-hit | Early calibration, unequal repeat counts | Superseded for aggregate claims. If useful as a trace illustration, verify the exact run IDs rather than mixing this calibration with pilot rows. |
| L04 | 643–655 | Long music-harmony control: cache reuse grows over execution; context pressure | Reported early trace; different from later named pilot run | Potential appendix trace after raw verification. Do not merge the 80-call trace with later 47-tool-call or 46-turn figures. Calls, turns, and tool calls are different counters. |
| L05 | 657–690 | Three proposed mechanisms: smaller prompt but more calls; cache reuse loss; repeated information acquisition | Hypotheses supported by local traces | Main explanation with measured counters. Avoid claiming all extra generation is state writing or all repeated calls are forgetting. |
| L06 | 695–709 | Original Table 1 token ratios repriced using local cache assumptions | Reconstructable sensitivity, not author cost | Appendix pricing sensitivity; formula and limitations below. The 0.97 proxy does not independently prove a short-task economic crossover. |
| L07 | 711–727 | Externally prescribed events versus agent-owned stopping; fixture uses 26 versus 43 calls | Conceptual distinction verified narrowly; fixture raw source unverified here | Main discussion of different evaluation questions. Restrict fixed-horizon criticism to synthetic scaling, not the original's interactive evaluations. No causal attribution of cross-paper performance solely to loop authority. |
| L08 | 731–789 | Complete tail sweep and reason for including 12 and infinity | Completed pilot axis; source conflates infinity with no-state baseline | Main window section and shared panels. Correct semantics: infinity is state plus all history. Verify whether retained unit is messages or exchanges for each implementation. |
| L09 | 791–841 | Hybrid means runtime-written facts plus semantic state, not state plus tail | Architectural intent; objective fields listed include proposals | Main Method/composition section. Only name fields actually emitted; runtime ownership prevents model overwrites of those fields, not all memory errors. |
| L10 | 845–889 | Network, credential lifetime, completeness, local inference alternatives | Infrastructure operations and plans | Exclude manuscript; final reproducibility protocol only. |
| L11 | 895–961 | Tail choice, disabled fallback, budget, schema choice, added facts/stop rule, stagnation threshold may confound conditions | Historical design audit | Extract legitimate Methods limitations and arm semantics. Do not describe a faithful reproduction where contracts differ; no chronology. |
| L12 | 963–991 | File-event and stale-state detector defects | Historical incidents, not experimental contribution | Exclude narrative; never infer measured coverage/staleness from dead counters. Preserve tests/provenance outside paper. |
| L13 | 995–1039 | Planned measurement sequence and then-current claims ready to write | Workflow + overbroad interim interpretation | Superseded; no independent evidence. In particular, two individual trajectories do not establish a horizon crossover. |
| L14 | 1045–1077 | First partial pilot: cost 2.35×, prompt 0.36×, cache delta −26.4 pp | Partial result | Superseded by complete pilot. Use complete rows rather than frozen partial summaries. |
| L15 | 1079–1101 | Short/mid/long partial cost ratios 2.90/1.38/1.85; non-monotone overhead | Partial descriptive stratification | Replace with complete fixed-cohort analysis. A ratio 1.38 is not a cost crossover; all three ratios exceed one. |
| L16 | 1103–1123 | Tail2 may lower cost despite worse cache-hit, suggesting saved re-acquisition outweighs input cost | Partial hypothesis, useful mechanism | Recover via completed window panels; cache-hit alone does not rank monetary efficiency. |
| L17 | 1127–1151 | First-repeat full sweep success by coarse horizon | Measured first-repeat snapshot | Superseded by all repeats for quality claims; retain repeat sensitivity if needed. |
| L18 | 1153–1187 | Withdrawn interior optimum; cobol trajectory suggests useful recent history | Early optimum retracted; cobol timeout labels later invalidated | Exclude optimum/timeout story. Direct full-repeat window contrasts determine whether a local plateau is supported. |
| L19 | 1189–1207 | Joint presentation of turns, money, peak, cache for a tail axis | Measured first-repeat economic panel | Use as table-design precedent, replace numbers with complete verified cohort. |
| L20 | 1209–1261 | Verdict and trajectory variability across repeats; possible instability effect | Interim measurement and hypothesis | Later repeat supersedes inference. Do not infer fixed reliability differences from selected examples. |
| L21 | 1265–1329 | Small sample and few discordances; screenshot shows equal task-level success counts for k6/12/∞ | Interim repeat aggregation not fully specified; not per-episode equality | Recompute episode rates and direct contrasts. `p=1` is not equivalence; selected pilot has a ceiling. |
| L22 | 1331–1359 | Two-repeat full-window cost/prompt comparison; continuous costs contain information binary outcomes miss | Measured snapshot; broad “any small evaluation is noise” overclaim | Complete three-repeat table supersedes. Precision discussion belongs in Methods/limitations, not a verdict on an entire literature. |
| L23 | 1363–1375 | State-only variability sign test p=.039 | Superseded/retracted at third repeat | Exclude significant-instability conclusion. |
| L24 | 1379–1529 | Timeout-censoring mechanism, censored success table, time-limit intervention, output per turn | Censoring interpretation explicitly retracted at 1679–1805 | Exclude entire causal timeout narrative. Output/token observations may be independently reanalysed without these labels. |
| L25 | 1533–1583 | Completed three-repeat window matrix; costs and prompt ratios across all five window sizes; cache-hit reductions | Completed pilot descriptive economics, `results/TABLES.txt` | Main window panels, supplementary repeat-level ratios; keep this cohort separate from the later full benchmark. |
| L26 | 1585–1619 | Three interim conclusions withdrawn | Mixed valid/invalid reasoning; subsequent correction overrides timeout rationale | Author evidence ledger only; manuscript reports final analyses, not retraction chronology. |
| L27 | 1621–1643 | Three-repeat verdict agreement by condition | Measured descriptive variability | Optional appendix if regenerated. Agreement is not a minimum detectable-effect threshold and not proof that arbitrary smaller population differences are unmeasurable. |
| L28 | 1645–1673 | Stronger-model pilot and claimed general methodological contribution | Later draft changes sample/values; broad conclusion unsupported | Quarantine stronger-model numbers until raw records reconciled; do not claim model strength cannot help. |
| L29 | 1679–1805 | Entire timeout section invalid; cost summaries independent of erroneous label; context pressure comparison | Retraction record plus retained observations | Exclude incident from paper; prevents resurrection of invalid claims. “36 tasks required” remains an inadequate power calculation. |
| L30 | 1809–1865 | Identical `(tool,args)` repetition metric, read-only subset, manual hard-task traces | Measured diagnostic definition | Main mechanism or appendix, with limits: same arguments need not mean same contents or useless work. |
| L31 | 1867–1897 | Full window sweep repetition medians reach control level by six; reported sign counts | `RESULT-redundant-work.md`; statistics count task-repeat cells | Valuable plateau evidence after task-clustered recalculation. Do not reuse the report's p-values as independent-task evidence. Repetition 1.27 implies a repeated-call fraction about 21%, not 25%. |
| L32 | 1899–1929 | Harder-task repetition and repeated-read extremes | Incomplete preview, `REDUNDANCY-tb4.txt` | Appendix case evidence only if desired; no population comparison or headline claim. |
| L33 | 1931–1951 | Context-pressure hypothesis explains why harder tasks might magnify repetition | Cross-corpus hypothesis, not controlled horizon experiment | Discussion; use new control-defined cohorts for within-corpus evidence. Task family/model difficulty differ across corpora. |
| L34 | 1953–1975 | Turn-budget completion asymmetry and exclusion from costs | Preview observation; proposed exclusion changes estimand | Define budget failures consistently. Report deployed-budget cost/quality on all outcomes; conditional successful-task costs are additional, not a replacement that removes expensive failures. |
| L35 | 1979–2039 | Control-median horizon, task as unit, median repeats; claimed detection threshold | Sound descriptive axis; threshold is not power | Methods should preserve the axis; discard overconfident threshold and sample-size claims. |
| L36 | 2043–2111 | Pilot task-level horizon/repetition values; rho .030, p .9256; no supported monotone trend | Reported complete task-level diagnostic | Optional appendix after recomputation. It is not evidence that all horizons behave alike. |
| L37 | 2113–2165 | Threshold-code incident and proposed larger/harder test | Incident + future design | Exclude incident. Preserve distinction between more tasks and greater context pressure in limitations. |

## Later manuscript generations: additions versus duplicates

These are prose drafts, not new experiment reports. Reading all versions is necessary because some contain information absent from the chronological portion, but their conclusions do not outrank data.

| Source span | Content and new leads | Admission decision |
|---|---|---|
| 2169–2334; 2539–2719 | First English/Russian abstract, introduction, methods, tail axis, original-paper comparison | Duplicates L02–L09. Adds explicit repricing assumptions (93%, 72%, 19.8%) and fixture/state-size claims. Preserve assumptions; verify fixture separately; reject faithful-reproduction and whole-paper fixed-T framing. |
| 2335–2380; 2721–2771 | Cost ratios; stronger-model pilot; continuous-cost power numbers | Economic ratios are duplicated measurements. Stronger-model sample changes from eight to seven and lacks inspected raw source; exclude generalized inference. |
| 2381–2402; 2773–2793 | Binary power and instability/timeout narratives | Historical and statistically overstated. No special “three trials guarantees truth” rule; no universal 36-task or 72-task minimum-power claim. |
| 2403–2460; 2795–2840 | Repair architecture, source ownership, no extra environment commands, no command suppression, token-budget confound, schema slopes | Useful Method/design detail. Ownership and implemented input records can be described; coverage/staleness counters and robustness slopes must not be represented as measured if they are not. Additional text can alter slopes as well as levels: the draft's “constant tokens only shift a curve” assertion is not generally valid. |
| 2461–2523; 2841–2903 | Measurement incidents, limitations, conclusion, reproduction appendix | Exclude incident-led narrative. Retain actual implementation/domain/model limitations and final inclusion rules once. Draft numerical total counts conflict and must never be copied. |
| 2525–2537; 2905–2921 | Original-paper reporting gaps | Verify each against primary source if used. Relevant gaps inform limited transfer claims, not an adversarial catalogue. |
| 2923–3084 | Second English draft before mechanism subsection | Repeats earlier prose; changes total records and claimed required tasks. The title “current” is historical, not authority over admitted later datasets. |
| 3085–3108; 3481–3504 | New repeated-call subsection | Same underlying L30–L36 reports, not replication. Carries the erroneous “25 tasks” unit and “one in four” interpretation. |
| 3109–3152; 3505–3545 | Repeated cost section plus hand-audited cache sequence | The per-turn sequence is a useful additional lead, available in `MECHANISM-fix-git.txt`; no new cohort. Keep exact trajectory correspondence and do not claim cache misses uniquely isolate state rewriting from window movement/prompt layout. |
| 3153–3184; 3547–3577 | Repeated power, retractions, completion modes | Same exclusions as above. Budget failure is a legitimate outcome under a specified budget, even though it does not prove unlimited-budget impossibility. |
| 3185–3230; 3579–3630 | Repeated hybrid/adaptive/schema/retrieval proposal | No new measurement. Distinguish currently evaluated runtime-record variants from untested archive and adaptive policy. |
| 3231–3331; 3631–3707 | Repeated incidents, limitations, conclusion, references; Russian duplicate starts at 3333 | No additional independent evidence. Final state must come from admitted data, not rhetorical strength or repetition across languages. |
| 3333–3480 | Second Russian draft abstract through original-paper comparison | Bilingual duplicate of 2923–3084, with the same overclaims; no new experiment. |

## Reconstructed original-table sensitivity: what the screenshot actually computes

Verified against [SKILL.state v3, Table 1 and §4.3](https://arxiv.org/html/2608.26263v3). The table reports total tokens without an input/cache/output decomposition. Its synthetic scaling horizon is externally generated; the paper also reports interactive InterCode and tau-bench results, so that distinction must not be generalized to the whole publication. [Primary source, §4–5 and Appendix B.2](https://arxiv.org/html/2608.26263v3).

The log's assumptions are `h_full=.93`, `h_state=.72`, `q=cache_price/input_price=.198` (lines 2303–2321 and 3055–3073). These are historical scenario inputs, not the cache-hit medians of the final experiments. Its proxy is:

```
discount(h, q) = (1-h) + q*h
discounted_proxy_ratio = published_total_token_ratio
                         * discount(.93,.198) / discount(.72,.198)
                      = published_total_token_ratio * 0.6014293828
```

| Exogenous event horizon | Published total-token ratio, full/state | Discounted-token proxy, full/state |
|---:|---:|---:|
| 10 | 1.607836 | 0.967000 |
| 25 | 2.901251 | 1.744897 |
| 50 | 5.693277 | 3.424104 |
| 100 | 19.040683 | 11.451626 |
| 200 | 21.316144 | 12.820155 |

The ratios are reconstructed, but **not a monetary reanalysis of the authors' episodes**: every reported token receives an input-cache discount, output is not separately priced, and cache-hit inputs come from another stack. The proxy shrinks the logical advantage to roughly 60% under these assumptions; it does not empirically establish full-cost parity at the shortest horizon. The old value 1.75 at the second horizon is approximate; direct recomputation rounds to 1.74 at two decimal places.

## Strongest defensible synthesis

The value of structured state is a smaller active memory, not a guarantee of lower execution cost or preserved capability. The observed penalties have separable contributors: additional generation, changed cache reuse, and repeated tool work. Runtime-maintained records address the cost of representing observable facts; a recent dialogue window addresses omissions in the local interaction sequence. The complete window pilot tests whether the latter repair has diminishing returns: repetition can reach its observed floor while larger windows continue to increase prompt size. This supports a **candidate local operating point**, not a universal optimal constant.

Cache-hit alone is not a cost ranking: a shorter context can have a lower hit fraction while processing fewer uncached tokens, and a larger window can save enough subsequent work to lower total cost. Therefore window size, solve rate, turns, uncached input, cached input, output, cache-hit, and money must remain jointly visible. Likewise, a cheaper incomplete trajectory is not the same estimand as cheaper successful completion.

Horizon analysis determines where those trade-offs differ across the observed task mix; it does not supply the unrun adaptive policy experiment. A conclusion should explicitly distinguish (a) implemented and measured repairs, (b) diagnostic evidence consistent with a mechanism, and (c) proposed archive/switching/schema-robustness extensions. This preserves the original engineering ambition without promoting a research plan, an incident, or an illustrative trajectory into a result.
