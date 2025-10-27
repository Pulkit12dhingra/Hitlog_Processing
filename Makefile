# Makefile for hitlog_processing

.PHONY: format requirements lint test commit

format:
	ruff format .

requirements:
	uv export --format=requirements.txt > requirements.txt

lint:
	ruff check .

test:
	pytest || test $$? -eq 5

commit: format requirements lint test
	@bash -c 'set -e; \
	git add . && \
	read -p "Enter commit message: " msg && \
	if [ -z "$msg" ]; then \
	  echo "Commit message cannot be blank."; exit 1; \
	fi && \
	git commit -m "$msg" && \
	git push'
