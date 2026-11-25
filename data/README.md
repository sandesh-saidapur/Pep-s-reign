# Data

- `raw/`: downloaded source files, exactly as fetched. Never edit these by hand. Re-download with `pep-reign ingest --refresh`.
- `processed/`: outputs of the pipeline (Parquet and CSV). Regenerate with `make data && make tables`.

Neither folder is committed to git. Only the code that produces them is.

Sources and their licences are listed in `docs/data-sources.md`.
