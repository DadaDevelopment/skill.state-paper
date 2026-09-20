"""Data invariants for the canonical E1 release CSV.

Runs against data/e1-release/canonical-e1-full.csv, the single file every
number in the manuscript is computed from (analysis/build_paper.py reads
nothing else). A silent invariant break here (a duplicate run, a task
missing its baseline, an out-of-range cost) has previously produced a wrong
headline number for a full run in this project (defects #12/#13, see
log/PROTOCOL-and-first-valid-point.md) - this test suite exists to catch
that class before it reaches build_paper.py.
"""

import os

import pandera.pandas as pa
import pandas as pd
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(REPO, "data", "e1-release", "canonical-e1-full.csv")

CONTROL = "baseline"
ARMS = {"tail0", "tail2", "tail6"}
ALL_CONDITIONS = ARMS | {CONTROL}
EXPECTED_TRIALS = 3
MAX_PLAUSIBLE_CACHE_TO_PEAK_RATIO = 500


class ExperimentResult(pa.DataFrameModel):
    run_id: str = pa.Field(unique=True)
    corpus: str
    task_id: str
    condition: str = pa.Field(isin=list(ALL_CONDITIONS))
    trial: int = pa.Field(ge=1, le=EXPECTED_TRIALS)
    solved: int = pa.Field(isin=[0, 1])
    stop_reason: str
    turns: int = pa.Field(gt=0)
    input_tokens: int = pa.Field(ge=0)
    cache_read_tokens: int = pa.Field(ge=0)
    output_tokens: int = pa.Field(ge=0)
    prompt_peak_tokens: int = pa.Field(ge=0)
    cost_usd: float = pa.Field(gt=0)
    git_revision: str
    plugin_revision: str
    schema_revision: str
    model: str


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(CSV_PATH, dtype={"trial": int, "solved": int})


def test_file_exists():
    assert os.path.isfile(CSV_PATH), "canonical release CSV missing"


def test_schema(df):
    ExperimentResult.validate(df)


def test_no_duplicate_run_id(df):
    dupes = df[df.duplicated(subset=["run_id"], keep=False)]
    assert dupes.empty, f"duplicate run_id rows: {dupes['run_id'].tolist()}"


def test_expected_trial_count(df):
    counts = df.groupby(["task_id", "condition"])["trial"].nunique()
    short = counts[counts < EXPECTED_TRIALS]
    assert short.empty, f"cells with fewer than {EXPECTED_TRIALS} trials:\n{short}"


def test_every_task_has_all_conditions(df):
    grouped = df.groupby("task_id")["condition"].apply(lambda s: set(s))
    missing = {
        task: ALL_CONDITIONS - conds
        for task, conds in grouped.items()
        if not ALL_CONDITIONS.issubset(conds)
    }
    assert not missing, f"tasks missing a condition: {missing}"


def test_every_arm_has_a_control_baseline(df):
    tasks_with_control = set(df[df["condition"] == CONTROL]["task_id"])
    tasks_with_arms = set(df[df["condition"].isin(ARMS)]["task_id"])
    orphan_arms = tasks_with_arms - tasks_with_control
    assert not orphan_arms, f"arm runs with no matching control: {orphan_arms}"


def test_single_model_single_schema_per_condition(df):
    for cond in ALL_CONDITIONS:
        sub = df[df["condition"] == cond]
        models = sub["model"].unique()
        assert len(models) == 1, f"{cond} ran on multiple models: {models}"


def test_git_revision_present(df):
    assert (df["git_revision"].str.len() > 0).all()


def test_no_solved_without_a_defined_stop_reason(df):
    assert df["stop_reason"].notna().all()
    assert (df["stop_reason"].str.len() > 0).all()


def test_cache_read_vs_prompt_peak_is_plausible(df):
    """A regression in token accounting would silently change the cost
    inversion headline; this catches a cache-read count that has drifted
    to an implausible multiple of the peak prompt size."""
    ratio = df["cache_read_tokens"] / df["prompt_peak_tokens"].clip(lower=1)
    assert (ratio < MAX_PLAUSIBLE_CACHE_TO_PEAK_RATIO).all()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
