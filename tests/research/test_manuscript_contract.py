import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/research"))
from manuscript_contract import GraphError, input_graph, source_findings, rendered_findings
from results_gate import check, find_bare_numbers


def project(tmp_path, setup="87 tasks; 174 matched executions.", result="A result."):
    for directory in ("paper", "paper-ru"):
        (tmp_path / directory / "sections").mkdir(parents=True)
        (tmp_path / directory / "main.tex").write_text(
            r"\input{sections/04_setup}\input{sections/06_results}")
        (tmp_path / directory / "sections/04_setup.tex").write_text(setup)
        (tmp_path / directory / "sections/06_results.tex").write_text(result)
    return tmp_path


def test_follows_active_graph_and_ignores_unused_legacy_section(tmp_path):
    root = project(tmp_path)
    (root / "paper/sections/obsolete.tex").write_text("E1: 174 pairs; 61.3 percent.")
    assert source_findings(root) == []
    assert check(root) == []


def test_missing_active_input_fails(tmp_path):
    root = project(tmp_path)
    (root / "paper/sections/06_results.tex").unlink()
    with pytest.raises(GraphError, match="Missing active input"):
        source_findings(root)


def test_input_wrapper_resolves_actual_table(tmp_path):
    main = tmp_path / "main.tex"
    (tmp_path / "tables").mkdir()
    table = tmp_path / "tables/current.tex"
    table.write_text("Table")
    main.write_text(r"\newcommand{\sharedtable}[1]{\input{tables/#1}}\sharedtable{current}")
    assert input_graph(main) == (main, table)


def test_macro_input_cannot_silently_disappear(tmp_path):
    main = tmp_path / "main.tex"
    main.write_text(r"\input{\unknown}")
    with pytest.raises(GraphError, match="Unresolved"):
        input_graph(main)


@pytest.mark.parametrize("text", ["E1 results", "V-axis results", "Rung only", "Control only",
                                  "160/261", "Использование ИИ", "Use of AI", "174 cases"])
def test_forbidden_reader_content_fails(tmp_path, text):
    assert source_findings(project(tmp_path, result=text))


def test_sample_sizes_must_share_one_methods_paragraph(tmp_path):
    assert source_findings(project(tmp_path, setup="87 tasks.\n\n174 executions."))


def test_comments_and_reference_arguments_do_not_count_as_prose(tmp_path):
    root = project(tmp_path, result=r"\ref{tab:E1} Result. % V-axis 174 pairs")
    assert source_findings(root) == []


def test_reference_on_same_line_cannot_hide_measured_number(tmp_path):
    path = tmp_path / "results.tex"
    path.write_text(r"The rate is 61.3\%, Table~\ref{tab:result}.")
    findings = find_bare_numbers(path)
    assert any(token == "61.3" for _, token, _ in findings)


def test_english_and_russian_active_results_are_both_guarded(tmp_path):
    root = project(tmp_path)
    (root / "paper-ru/sections/06_results.tex").write_text("Получено 61.3 процента.")
    assert len(check(root)) == 1


def test_all_active_table_names_are_checked_for_language(tmp_path):
    root = project(tmp_path)
    (root / "paper/tables").mkdir()
    (root / "paper/tables/not-prefixed.tex").write_text("Условие & Solved rate")
    with (root / "paper/main.tex").open("a") as handle:
        handle.write(r"\input{tables/not-prefixed}")
    assert any("Cyrillic" in finding for finding in source_findings(root))


def test_rendered_output_must_be_nonempty_and_both_languages(tmp_path):
    (tmp_path / "build/research").mkdir(parents=True)
    (tmp_path / "build/research/manuscript.txt").write_text("English")
    with pytest.raises(GraphError, match="missing"):
        rendered_findings(tmp_path)
