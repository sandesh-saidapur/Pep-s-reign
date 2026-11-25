"""Compare each team with its own league, season by season.

Raw totals depend on how strong a league was in a given year. These helpers
express each team's per-game figures against that season's average and rank.
"""

from __future__ import annotations

import pandas as pd

from pep_reign.config import BASELINE_SEASONS, SEASONS

CONTEXT_METRICS = [
    "points_per_game",
    "shots_for_per_game",
    "shots_against_per_game",
    "shots_on_target_for_per_game",
]


def add_era(tables: pd.DataFrame) -> pd.DataFrame:
    """Label each season as 'baseline' (pre-Pep) or 'pep'."""
    out = tables.copy()
    out["era"] = out["season"].map(
        lambda s: "pep" if s in SEASONS else ("baseline" if s in BASELINE_SEASONS else "other")
    )
    return out


def add_points_per_game(tables: pd.DataFrame) -> pd.DataFrame:
    out = tables.copy()
    out["points_per_game"] = out["points"] / out["played"]
    return out


def add_league_context(tables: pd.DataFrame) -> pd.DataFrame:
    """For each metric, add the season average, the team's gap to it, and its rank.

    Rank 1 is the highest value in that season. For shots conceded, rank 1 means
    conceding the most, so read it as a 'how exposed' rank, not a quality rank.
    """
    out = tables.copy()
    for metric in CONTEXT_METRICS:
        grouped = out.groupby("season")[metric]
        out[f"{metric}_league_avg"] = grouped.transform("mean")
        out[f"{metric}_vs_league"] = out[metric] - out[f"{metric}_league_avg"]
        out[f"{metric}_rank"] = grouped.rank(ascending=False, method="min").astype(int)
    return out


def era_summary(city_seasons: pd.DataFrame) -> pd.DataFrame:
    """Average City's per-game figures by era (baseline vs Pep)."""
    columns = ["points_per_game", *[f"{m}_vs_league" for m in CONTEXT_METRICS[1:]]]
    return city_seasons.groupby("era")[columns].mean().reset_index()
