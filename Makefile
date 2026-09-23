.PHONY: audit audit-ru paper paper-ru prose prose-ru references data results literature links review manuscript clean

paper:
	sh paper/build.sh

prose:
	sh scripts/research/extract_text.sh
	npx slop check build/research/manuscript-prose.txt --max-per-1000 0
	. .venv-research/bin/activate && python3 scripts/research/slop_gate.py

references:
	. .venv-research/bin/activate && python3 scripts/research/check_bib_format.py
	sh scripts/research/run_refcheck.sh
	. .venv-research/bin/activate && python3 scripts/research/refcheck_gate.py

data:
	. .venv-research/bin/activate && python3 -m pytest -q tests/research/

results:
	. .venv-research/bin/activate && python3 scripts/research/results_gate.py

literature:
	. .venv-research/bin/activate && python3 scripts/research/literature_gate.py

links:
	. .venv-research/bin/activate && python3 scripts/research/check_links.py

review:
	. .venv-research/bin/activate && python3 scripts/research/llm_review.py
	@echo "review requires a dispatched independent subagent - see build/research/review-bundle.json"

paper-ru:
	sh paper-ru/build.sh

prose-ru:
	sh scripts/research/extract_text_ru.sh
	. .venv-research/bin/activate && python3 scripts/research/slop_check_ru.py

manuscript: prose prose-ru
	. .venv-research/bin/activate && python3 scripts/research/manuscript_contract.py --rendered

audit: paper paper-ru manuscript references data results literature links

audit-ru: paper-ru prose-ru

clean:
	rm -rf build/research
