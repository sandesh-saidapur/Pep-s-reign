"""Build league tables from match results."""

from __future__ import annotations

import pandas as pd

TABLE_COLUMNS = [
    "season",
    "position",
    "team",
    "played",
    "won",
    "drawn",
    "lost",
    "goals_for",
    "goals_against",
    "goal_difference",
    "points",
]


def _long_form(matches: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match, so home and away results share one code path."""
    home = pd.DataFrame(
        {
            "season": matches["season"],
            "team": matches["home"],
            "goals_for": matches["home_goals"],
            "goals_against": matches["away_goals"],
        }
    )
    away = pd.DataFrame(
        {
            "season": matches["season"],
            "team": matches["away"],
            "goals_for": matches["away_goals"],
            "goals_against": matches["home_goals"],
        }
    )
    long = pd.concat([home, away], ignore_index=True)
    long["won"] = (long["goals_for"] > long["goals_against"]).astype(int)
    long["drawn"] = (long["goals_for"] == long["goals_against"]).astype(int)
    long["lost"] = (long["goals_for"] < long["goals_against"]).astype(int)
    long["points"] = 3 * long["won"] + long["drawn"]
    return long


def league_tables(matches: pd.DataFrame) -> pd.DataFrame:
    """Compute a final table per season, ranked by points, then goal difference, then goals scored.

    This is a simplified ranking. It does not model head-to-head tie-breaks, which
    matter only when teams finish level on all three criteria.
    """
    long = _long_form(matches)
    grouped = long.groupby(["season", "team"], as_index=False).agg(
        played=("points", "size"),
        won=("won", "sum"),
        drawn=("drawn", "sum"),
        lost=("lost", "sum"),
        goals_for=("goals_for", "sum"),
        goals_against=("goals_against", "sum"),
        points=("points", "sum"),
    )
    grouped["goal_difference"] = grouped["goals_for"] - grouped["goals_against"]

    ranked = grouped.sort_values(
        ["season", "points", "goal_difference", "goals_for"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)
    ranked["position"] = ranked.groupby("season").cumcount() + 1
    return ranked[TABLE_COLUMNS]


def team_season(tables: pd.DataFrame, team: str) -> pd.DataFrame:
    """Return one club's season lines, in season order."""
    return tables.loc[tables["team"] == team].sort_values("season").reset_index(drop=True)
