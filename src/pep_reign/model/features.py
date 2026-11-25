"""Leakage-safe pre-match features from each team's recent form.

For every match, a team's features use only matches that finished before it.
That is enforced by shifting each team's history by one match before taking a
rolling mean, so a match's own result never leaks into its own features.
"""

from __future__ import annotations

import pandas as pd

FORM_COLUMNS = ["form_points", "form_shots_for", "form_shots_against", "form_sot_for"]
MIN_HISTORY = 3  # matches of history needed before a team's form is used
WINDOW = 5  # number of recent matches in the rolling form


def _team_rows(matches: pd.DataFrame) -> pd.DataFrame:
    """One row per team per match, tagged with the match id and whether the team was home."""
    base = {"match_id": matches.index, "date": matches["date"]}
    home = pd.DataFrame(
        {
            **base,
            "side": "home",
            "team": matches["home"],
            "goals_for": matches["home_goals"],
            "goals_against": matches["away_goals"],
            "shots_for": matches["home_shots"],
            "shots_against": matches["away_shots"],
            "sot_for": matches["home_shots_on_target"],
        }
    )
    away = pd.DataFrame(
        {
            **base,
            "side": "away",
            "team": matches["away"],
            "goals_for": matches["away_goals"],
            "goals_against": matches["home_goals"],
            "shots_for": matches["away_shots"],
            "shots_against": matches["home_shots"],
            "sot_for": matches["away_shots_on_target"],
        }
    )
    rows = pd.concat([home, away], ignore_index=True)
    rows["points"] = (rows["goals_for"] > rows["goals_against"]) * 3 + (
        rows["goals_for"] == rows["goals_against"]
    ) * 1
    return rows.sort_values(["date", "match_id"], kind="stable").reset_index(drop=True)


def rolling_form(matches: pd.DataFrame) -> pd.DataFrame:
    """Form before each match, indexed by (match_id, side). NaN when history is short."""
    rows = _team_rows(matches)
    sources = {
        "form_points": "points",
        "form_shots_for": "shots_for",
        "form_shots_against": "shots_against",
        "form_sot_for": "sot_for",
    }
    grouped = rows.groupby("team", sort=False)
    for target, column in sources.items():
        rows[target] = grouped[column].transform(
            lambda s: s.shift(1).rolling(WINDOW, min_periods=MIN_HISTORY).mean()
        )
    return rows.set_index(["match_id", "side"])[FORM_COLUMNS].sort_index()


def build_features(matches: pd.DataFrame) -> pd.DataFrame:
    """One row per match: both teams' form, their differences, and the result.

    `matches` must have a unique index, which becomes the match id. Matches where
    either team lacks MIN_HISTORY prior matches are dropped.
    """
    if not matches.index.is_unique:
        raise ValueError("matches must have a unique index")

    form = rolling_form(matches)
    home = form.xs("home", level="side").add_suffix("_home")
    away = form.xs("away", level="side").add_suffix("_away")
    base = ["season", "date", "home", "away", "home_goals", "away_goals"]
    frame = matches[base + [c for c in ODDS_COLUMNS if c in matches.columns]]
    frame = frame.join(home, how="inner").join(away, how="inner")

    for name in FORM_COLUMNS:
        frame[f"{name}_diff"] = frame[f"{name}_home"] - frame[f"{name}_away"]
    frame["outcome"] = _outcome(frame["home_goals"], frame["away_goals"])
    return frame.dropna(subset=FEATURE_COLUMNS)


def _outcome(home_goals: pd.Series, away_goals: pd.Series) -> pd.Series:
    outcome = pd.Series("D", index=home_goals.index)
    outcome[home_goals > away_goals] = "H"
    outcome[home_goals < away_goals] = "A"
    return outcome


FEATURE_COLUMNS = [f"{c}_diff" for c in FORM_COLUMNS]
ODDS_COLUMNS = ["home_odds", "draw_odds", "away_odds"]
