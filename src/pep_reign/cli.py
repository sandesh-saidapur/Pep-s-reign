"""Command-line entry points: `pep-reign ingest` and `pep-reign tables`."""

from __future__ import annotations

import pandas as pd
import typer

from pep_reign.config import CLUB, PROCESSED_DIR, SEASONS
from pep_reign.ingest.openfootball import load_seasons
from pep_reign.transform.tables import league_tables, team_season
from pep_reign.validate import MATCH_SCHEMA, check_matches_complete

app = typer.Typer(help="Manchester City under Pep Guardiola: data pipeline.")


@app.command()
def ingest(refresh: bool = typer.Option(False, help="Re-download cached season files.")) -> None:
    """Download and validate PL results for Pep's seasons, then save them as Parquet."""
    matches = load_seasons(SEASONS, refresh=refresh)
    MATCH_SCHEMA.validate(matches)
    check_matches_complete(matches)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "pl_matches.parquet"
    matches.to_parquet(out, index=False)
    typer.echo(f"wrote {len(matches)} matches to {out}")


@app.command()
def tables() -> None:
    """Build league tables and City's season summary from the processed matches."""
    matches_path = PROCESSED_DIR / "pl_matches.parquet"
    if not matches_path.exists():
        typer.echo("no processed matches yet; run `pep-reign ingest` first", err=True)
        raise typer.Exit(code=1)

    matches = pd.read_parquet(matches_path)
    all_tables = league_tables(matches)
    all_tables.to_csv(PROCESSED_DIR / "pl_tables.csv", index=False)
    team_season(all_tables, CLUB).to_csv(PROCESSED_DIR / "city_seasons.csv", index=False)
    typer.echo(f"wrote tables for {all_tables['season'].nunique()} seasons")


if __name__ == "__main__":
    app()
