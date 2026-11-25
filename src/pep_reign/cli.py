"""Command-line entry points: `pep-reign ingest`, `shots` and `tables`."""

from __future__ import annotations

import pandas as pd
import typer

from pep_reign.config import ALL_SEASONS, CLUB, PROCESSED_DIR
from pep_reign.ingest import football_data
from pep_reign.ingest.openfootball import load_seasons
from pep_reign.transform.league_context import (
    add_era,
    add_league_context,
    add_points_per_game,
    era_summary,
)
from pep_reign.transform.reconcile import check_scores_agree
from pep_reign.transform.shots import add_per_game_shots, shot_totals
from pep_reign.transform.tables import league_tables, team_season
from pep_reign.validate import MATCH_SCHEMA, check_matches_complete

app = typer.Typer(help="Manchester City under Pep Guardiola: data pipeline.")


@app.command()
def ingest(refresh: bool = typer.Option(False, help="Re-download cached season files.")) -> None:
    """Download and validate PL results for Pep's seasons, then save them as Parquet."""
    matches = load_seasons(ALL_SEASONS, refresh=refresh)
    MATCH_SCHEMA.validate(matches)
    check_matches_complete(matches)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "pl_matches.parquet"
    matches.to_parquet(out, index=False)
    typer.echo(f"wrote {len(matches)} matches to {out}")


@app.command()
def shots(refresh: bool = typer.Option(False, help="Re-download cached season files.")) -> None:
    """Download Football-Data match stats, cross-check scores against openfootball, save them."""
    primary_path = PROCESSED_DIR / "pl_matches.parquet"
    if not primary_path.exists():
        typer.echo("no processed matches yet; run `pep-reign ingest` first", err=True)
        raise typer.Exit(code=1)

    primary = pd.read_parquet(primary_path)
    secondary = football_data.load_seasons(ALL_SEASONS, refresh=refresh)
    joined = check_scores_agree(primary, secondary)
    out = PROCESSED_DIR / "football_data_matches.parquet"
    secondary.to_parquet(out, index=False)
    typer.echo(f"scores agree on {len(joined)} matches; wrote {out}")


@app.command()
def tables() -> None:
    """Build league tables and City's season summary, with shot rates when available."""
    matches_path = PROCESSED_DIR / "pl_matches.parquet"
    if not matches_path.exists():
        typer.echo("no processed matches yet; run `pep-reign ingest` first", err=True)
        raise typer.Exit(code=1)

    matches = pd.read_parquet(matches_path)
    all_tables = league_tables(matches)

    shots_path = PROCESSED_DIR / "football_data_matches.parquet"
    if shots_path.exists():
        shot_frame = pd.read_parquet(shots_path)
        all_tables = add_per_game_shots(all_tables, shot_totals(shot_frame))
    else:
        typer.echo("no shot data yet; run `pep-reign shots` for shot rates")

    all_tables = add_league_context(add_points_per_game(all_tables))
    all_tables = add_era(all_tables)
    all_tables.to_csv(PROCESSED_DIR / "pl_tables.csv", index=False)

    city = team_season(all_tables, CLUB)
    city.to_csv(PROCESSED_DIR / "city_seasons.csv", index=False)
    era_summary(city).to_csv(PROCESSED_DIR / "city_era_summary.csv", index=False)
    typer.echo(f"wrote tables for {all_tables['season'].nunique()} seasons")


if __name__ == "__main__":
    app()
