.PHONY: install install-extras data shots tables test lint format typecheck app check

# Core, dev and ML dependencies, as used by the tests and CI. The dashboard extra is
# installed separately with install-extras.
install:
	uv sync --extra ml

install-extras:
	uv sync --extra ml --extra app

data:
	uv run pep-reign ingest

shots:
	uv run pep-reign shots

tables:
	uv run pep-reign tables

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

app:
	uv run streamlit run dashboards/app.py

check: lint typecheck test
