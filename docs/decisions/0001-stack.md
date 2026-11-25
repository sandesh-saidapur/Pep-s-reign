# 0001: Tooling stack

Status: accepted (Nov 2026)

## Context

The project is a portfolio piece for AI, data science and ML roles. Job postings in 2026 repeatedly ask for Python, SQL, pandas, scikit-learn, PyTorch or TensorFlow, MLflow, Docker, and Git-based workflows. Some ask for Spark, Databricks, or a cloud platform, which this project does not need.

## Decision

- **Python 3.11+ with uv** for environments and locking. uv is fast and produces a lockfile that CI can use.
- **pandas and Parquet** for the core pipeline. DuckDB is included for SQL-style analysis without a server.
- **pandera** validates every stage. Schema checks are a common expectation in production data work.
- **pytest, ruff, mypy, pre-commit, GitHub Actions** for quality gates.
- **scikit-learn and XGBoost** for modelling, **MLflow** for experiment tracking, in an optional extra.
- **Streamlit** for the dashboard, in an optional extra.
- **Docker** for a reproducible test environment.

## Not chosen (yet)

- **PyTorch and TensorFlow.** Frequently listed, but the data is small tabular data where gradient-boosted trees are the right tool. Revisit if the project adds a sequence or image model.
- **Spark and Databricks.** The data fits in memory by orders of magnitude. Add only if a later stage needs it.
- **Airflow, Prefect or Dagster.** Orchestration matters once there are scheduled jobs. The CLI covers this scale.
- **dbt.** Useful for warehouse-style SQL models. Not needed for local Parquet files.

## Consequences

Each tool earns its place in a pipeline a reviewer can read in one sitting. Stretch tools live in optional extras, so the base install stays light.
