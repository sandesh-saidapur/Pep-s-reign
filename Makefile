.PHONY: install data tables test lint format typecheck app check

install:
	uv sync --all-extras

data:
	uv run pep-reign ingest

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
