

VERSION=`uv version --short`


.PHONY: reset
reset:
	rm -r ./.venv || true
	rm uv.lock || true


.PHONY: mdformat
mdformat:
	uv run mdformat *.md

.PHONY: mdformat-check
mdformat-check:
	uv run mdformat --check *.md

.PHONY: mypy
mypy:
	uv run mypy src

.PHONY: install_dev
install_dev:
	uv sync --group dev


.PHONY: test
test:
	uv run pytest tests --cov=src --cov-report term-missing --durations 5


.PHONY: lint
lint:
	uv run ruff check --output-format=full
	uv run ruff format --diff
	$(MAKE) mdformat-check
	$(MAKE) mypy

.PHONY: format
format:
	uv run ruff format
	uv run ruff check --fix
	$(MAKE) mdformat

.PHONY: test-all
test-all:
	$(MAKE) lint
	$(MAKE) test


.PHONY: document
document:
	rm -rf docs/source/reference/generated || true
	rm -rf public/*
	uv run sphinx-build -b html docs/source public/
