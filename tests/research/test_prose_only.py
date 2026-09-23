import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/research"))
from prose_only import prose_only


def test_removes_table_cells_but_retains_caption_and_surrounding_prose():
    source = r"""Before.
\begin{table}
\caption{A meaningful caption.}
\begin{tabular}{lr}
Approach & -- \\
\end{tabular}
\end{table}
After.
"""
    extracted = prose_only(source)
    assert "meaningful caption" in extracted
    assert "Before." in extracted and "After." in extracted
    assert "Approach" not in extracted and "--" not in extracted
    assert extracted.count("\n") == source.count("\n")


@pytest.mark.parametrize("environment", ["tabularx", "tikzpicture", "algorithmic"])
def test_nested_nonprose_environments_are_removed(environment):
    source = rf"\begin{{{environment}}}\begin{{scope}}x\end{{scope}}\end{{{environment}}}Prose"
    assert prose_only(source).strip() == "Prose"


def test_math_and_prose_are_not_silenced():
    source = r"The cost falls. \begin{equation}D=\alpha U\end{equation} Explain the result."
    assert prose_only(source) == source


@pytest.mark.parametrize("source", [r"\begin{tabular}broken", r"\end{tikzpicture}",
                                    r"\begin{tabular}\end{table}"])
def test_malformed_environment_fails_closed(source):
    with pytest.raises(ValueError):
        prose_only(source)
