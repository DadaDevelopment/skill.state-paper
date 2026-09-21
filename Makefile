.PHONY: audit paper prose references data results review clean

paper:
	sh paper/build.sh

prose:
	sh scripts/research/extract_text.sh
	npx slop check build/research/manuscript.txt --max-per-1000 0
	. .venv-research/bin/activate && python3 scripts/research/slop_gate.py

references:
	npx bibtex-tidy paper/references.bib --duplicates=doi,key,citation -m
	git diff --exit-code -- paper/references.bib
	sh scripts/research/run_refcheck.sh
	. .venv-research/bin/activate && python3 scripts/research/refcheck_gate.py

data:
	. .venv-research/bin/activate && python3 -m pytest -q tests/research/

results:
	. .venv-research/bin/activate && python3 scripts/research/results_gate.py

literature:
	. .venv-research/bin/activate && python3 scripts/research/literature_gate.py

links:
	lychee --no-progress README.md paper/README.md docs/ design/ results/

review:
	. .venv-research/bin/activate && python3 scripts/research/llm_review.py
	@echo "review requires a dispatched independent subagent - see build/research/review-bundle.json"

paper-ru:
	sh paper-ru/build.sh

prose-ru:
	sh scripts/research/extract_text_ru.sh
	. .venv-research/bin/activate && python3 scripts/research/slop_check_ru.py

audit: paper prose references data results literature links

audit-ru: paper-ru prose-ru

clean:
	rm -rf build/research
