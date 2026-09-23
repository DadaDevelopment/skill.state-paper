# Historical cache-discount sensitivity

This is a reproducible **scenario**, not experimental billing data. Published means from [SKILL.state v3 Table 1](https://arxiv.org/html/2608.26263v3#S4.T1) are multiplied by a cache-discount ratio using historical log assumptions: full-history cache-hit 0.93, state cache-hit 0.72, cache/input price ratio 0.198. The exact input values and provenance are in `source.json`.

For `d(h,q) = 1-h+q*h`, the generated proxy is `total_tokens_full / total_tokens_state * d(.93,.198) / d(.72,.198)`. The multiplier is approximately 0.601429. Direction is **full history divided by state**; a value above one favors state only under this proxy.

The publication does not supply the input/cache/output decomposition needed to reconstruct an invoice. This scenario effectively treats all reported tokens as cacheable input; it cannot recover output cost or establish the authors' actual cache-hit rate. The historical cache assumptions are not the aggregate cache-hit measurements of our final comparisons. Consequently, the near-parity value at the shortest horizon is a sensitivity illustration, not observed cost crossover or an independent experimental confirmation.

The old log rounds the second proxy to 1.75. Direct calculation from the published mean token totals produces 1.744897, displayed as 1.74. Source tables contain means and standard deviations, but this deterministic transformation of the means does not generate an uncertainty interval.

Run `python analysis/build_pricing_sensitivity.py`, followed by `python analysis/build_pricing_sensitivity.py --check`. The resulting English table and macros are shared by both manuscripts. No raw run counts, monetary-cost columns, or significance tests are generated for this scenario.
