"""Shot-based team metrics from match-level shot counts."""

from __future__ import annotations

import pandas as pd

SHOT_TOTAL_COLUMNS = [
    "shots_for",
    "shots_against",
    "shots_on_target_for",
    "shots_on_target_against",
]


def shot_totals(matches: pd.DataFrame) -> pd.DataFrame:
    """Sum each team's shots for and against per season.

    Expects columns: season, home, away, home_shots, away_shots,
    home_shots_on_target, away_shots_on_target.
    """
    home = pd.DataFrame(
        {
            "season": matches["season"],
            "team": matches["home"],
            "shots_for": matches["home_shots"],
            "shots_against": matches["away_shots"],
            "shots_on_target_for": matches["home_shots_on_target"],
            "shots_on_target_against": matches["away_shots_on_target"],
        }
    )
    away = pd.DataFrame(
        {
            "season": matches["season"],
            "team": matches["away"],
            "shots_for": matches["away_shots"],
            "shots_against": matches["home_shots"],
            "shots_on_target_for": matches["away_shots_on_target"],
            "shots_on_target_against": matches["home_shots_on_target"],
        }
    )
    long = pd.concat([home, away], ignore_index=True)
    return long.groupby(["season", "team"], as_index=False)[SHOT_TOTAL_COLUMNS].sum()


def add_per_game_shots(table: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
    """Join shot totals onto a league table and add per-game rates.

    Raises if any table row has no shot data, so a join gap cannot pass silently.
    """
    merged = table.merge(totals, on=["season", "team"], how="left", validate="one_to_one")
    missing = merged[SHOT_TOTAL_COLUMNS].isna().any(axis=1)
    if missing.any():
        gaps = merged.loc[missing, ["season", "team"]].values.tolist()
        raise ValueError(f"no shot data for: {gaps}")

    for column in SHOT_TOTAL_COLUMNS:
        merged[f"{column}_per_game"] = merged[column] / merged["played"]
    return merged
