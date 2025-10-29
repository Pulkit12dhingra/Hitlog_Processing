# Makefile for hitlog_processing

.PHONY: format requirements lint test commit push

format:
	ruff format .

requirements:
	uv pip compile pyproject.toml --no-reuse-hashes --output-file=requirements.txt

lint:
	ruff check . --exclude notebooks

test:
	pytest 

commit: format requirements lint test
	@bash -c '{ \
	set -e; \
	git add .; \
	read -p "Enter commit message: " msg; \
	echo "DEBUG: Entered message: [$${msg}]"; \
	if [ -z "$$(echo $${msg} | tr -d "[:space:]")" ]; then \
	  echo "Commit message cannot be blank or whitespace."; exit 1; \
	fi; \
	git commit -m "$${msg}"; \
	git push; \
}'

push: lint test
	@bash -c '{ \
	set -e; \
	git add .; \
	read -p "Enter commit message: " msg; \
	echo "DEBUG: Entered message: [$${msg}]"; \
	if [ -z "$$(echo $${msg} | tr -d "[:space:]")" ]; then \
	  echo "Commit message cannot be blank or whitespace."; exit 1; \
	fi; \
	git commit -m "$${msg}"; \
	git push; \
}'