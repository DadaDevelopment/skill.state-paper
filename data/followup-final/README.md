# Final aggregate release for the hybrid-memory comparisons

This table transcribes the final two-repeat report and the user's final token
corrections. It supersedes the earlier trial-only data in `data/v-axis/` for the
final comparisons. Complete first-repeat composition rows are retained only in
a separately labeled exploratory analysis; see `data/v-axis/README.md`.
Source: supplied `FULL-REPORT-vaxis-t1t2.md`, with median
input/output/cache values taken from the user's later message where they differ
by one token. Source-level arm identifiers are retained only for traceability;
the paper names the approaches being compared.

This is aggregate evidence, not a raw-run release. The generator validates
outcome margins and every supplied discordance table. It cannot verify missing
runs, trial alignment, per-task variability, or runtime implementation fidelity.
Exact McNemar reference p-values can be calculated from the supplied discordant
counts. These are not task-cluster-robust confidence statements. No bootstrap
intervals, peak-prompt statistics, or total-token efficiencies are reconstructed
for this release.

Cost totals are rounded to cents and their sum is 30.76 USD, whereas the report
states 30.77 USD. They are not silently rescaled. Mean cost and solved-per-dollar
values calculated from these totals are approximate. Median costs are the
reported medians, not recomputed from the totals. All costs use the study's
normalized tariff, not actual provider invoices.

The `hybrid-v7` row is the reference for the protocol/schema and failure-record
contrasts. The `control` row is the full-history reference for the hybrid-memory
history-window comparison. Neither is pooled with the earlier model-written
memory study. The control and richer composition configurations from the first
repeat also appear in the exploratory table and are explicitly identified as
overlapping evidence, not an independent replication.
