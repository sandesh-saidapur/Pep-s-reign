.PHONY: install install-extras data shots tables test lint format typecheck app check

# Core and dev dependencies only. Optional extras are installed separately (see install-extras)
# because some of their transitive packages lack wheels for every Python version.
install:
	uv sync

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
