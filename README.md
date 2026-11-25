# Pep's reign: Manchester City under Pep Guardiola

An analytics and machine learning project asking how good Manchester City really were between 2016/17 and 2024/25, using only free, trusted data.

## Questions

1. How did City's points, goals, and league position change across Pep's nine seasons?
2. How dominant were they compared with the rest of the Premier League, and with their own pre-Pep baseline?
3. (Stretch) Did City's finishing beat or lag expected goals, and how much did key absences change results?

The full plan is in [`docs/project-plan.md`](docs/project-plan.md). Data sources, licences and their limits are in [`docs/data-sources-and-week1.md`](docs/data-sources-and-week1.md).

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
make install   # create the virtual environment and install dependencies
make data      # download and validate PL results for 2016/17 to 2024/25
make tables    # build league tables and City's season summary
make check     # lint, type-check and run the tests
make app       # open the Streamlit dashboard
```

To install the optional machine learning and dashboard extras: `uv sync --extra ml --extra app`.

## Stack

| Area | Tools | Why |
|---|---|---|
| Language and data | Python, pandas, NumPy, DuckDB, Parquet | The core stack in data science and ML job postings |
| Data validation | pandera | Schema checks at each pipeline stage, so bad input fails loudly |
| Modelling (stretch) | scikit-learn, XGBoost | Standard tabular ML tools |
| Experiment tracking (stretch) | MLflow | Tracking and model registry, a common requirement in ML roles |
| Dashboard | Streamlit | Quick interactive data apps |
| Packaging and environment | uv, pyproject.toml, Docker | Reproducible installs and a portable test environment |
| Quality | pytest, ruff, mypy, pre-commit | Tests and style checks, which ML teams expect in code review |
| CI | GitHub Actions | Runs lint, types and tests on every push |

## Repository layout

```
src/pep_reign/        pipeline code: ingest, transform, validate, CLI
tests/                unit tests and small fixtures cut from real results
dashboards/           Streamlit app
notebooks/            exploration only; analysis logic lives in src/
docs/                 project plan, data sources, decision records
data/                 raw and processed data (not committed)
```

## Data and licences

Results come from [openfootball](https://github.com/openfootball/england), which is public domain. Other sources and their limits are listed in `docs/data-sources-and-week1.md`. Publish derived numbers, not raw dumps.
