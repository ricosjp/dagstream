

VERSION=`poetry version --short`

.PHONY: mdformat
mdformat:
	poetry run mdformat *.md

.PHONY: mdformat-check
mdformat-check:
	poetry run mdformat --check *.md

.PHONY: mypy
mypy:
	poetry run mypy src

.PHONY: install_dev
install_dev:
	poetry install --sync --with dev


.PHONY: test
test:
	poetry run pytest tests --cov=src --cov-report term-missing --durations 5


.PHONY: lint
lint:
	poetry run python3 -m ruff check --output-format=full
	poetry run python3 -m ruff format --diff
	$(MAKE) mdformat-check
	$(MAKE) mypy

.PHONY: format
format:
	poetry run python3 -m ruff format
	poetry run python3 -m ruff check --fix
	$(MAKE) mdformat

.PHONY: test-all
test-all:
	$(MAKE) lint
	$(MAKE) test


.PHONY: document
document:
	rm -rf docs/source/reference/generated || true
	rm -rf public/*
	poetry run sphinx-build -b html docs/source public/
