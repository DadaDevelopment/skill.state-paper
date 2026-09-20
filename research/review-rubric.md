# Research review rubric

What an independent reviewer of this manuscript is checked against before
a change lands on `main`. Mirrors the categories `llm_review.py` sends to
the isolated reviewer subagent.

## Hard fails (BLOCKER or MAJOR)

- A claim in the abstract, results, or conclusion is not backed by a macro
  from `paper/generated/numbers.tex` or `paper/generated/composition.tex`.
- A reference is unresolved, has a DOI/title/author mismatch, or is flagged
  retracted, and has no waiver.
- A statistical claim (significance, effect size, power) does not match
  what `analysis/build_paper.py --check` recomputes from the canonical CSV.
- A relevant paper discovered by the literature watch is untriaged.
- The manuscript makes an overclaim: a scope wider than the measured
  regime (model, corpus, horizon) supports.

## Reported, not blocking (MINOR)

- Prose style issues below the zero-slop threshold's structural findings
  (i.e. things already covered by `make prose` are not re-litigated here).
- Missing-literature suggestions where the paper's own citation already
  covers the same ground under a different name.

## Independence requirement

The reviewer must not share this session's context, reasoning, or prior
turns with the writer. `llm_review.py` packages the manuscript, refcheck
output, and literature candidates into `build/research/review-bundle.json`
specifically so the review can be dispatched to an isolated subagent that
reads only those files - this has already caught one real defect in this
manuscript (a cost claim computed from an aggregate the paper's own
methodology section disqualifies; see git history around the "Blind
review fixes" commit).
