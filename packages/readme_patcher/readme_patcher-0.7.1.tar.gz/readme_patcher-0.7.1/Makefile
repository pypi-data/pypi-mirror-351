all: test format docs lint type_check

test:
	uv run --isolated --python=3.8 pytest
	uv run --isolated --python=3.9 pytest
	uv run --isolated --python=3.10 pytest
	uv run --isolated --python=3.11 pytest
	uv run --isolated --python=3.12 pytest
	uv run --isolated --python=3.13 pytest

test_quick:
	uv run --isolated --python=3.12 pytest

install: update

# https://github.com/python-poetry/poetry/issues/34#issuecomment-1054626460
# pip install --editable . # error: externally-managed-environment -> pipx
install_editable:
	pipx install --force --editable .

update: clear_poetry_cache
	poetry lock
	poetry install

build:
	uv build

publish:
	uv build
	uv publish

format:
	uv run ruff check --select I --fix .
	uv run ruff format

docs:
	uv run --isolated --python=3.13 readme-patcher

lint:
	uv run ruff check

type_check:
	uv run mypy readme_patcher tests

.PHONY: test install install_editable update build publish format docs lint pin_docs_requirements
