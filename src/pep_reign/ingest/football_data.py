"""Download and parse Premier League match data from Football-Data.co.uk.

Football-Data gives full-time goals plus shots and shots on target for each match.
It does not give xG; Understat is the planned xG source.
"""

from __future__ import annotations

import io
from pathlib import Path

import httpx
import pandas as pd

from pep_reign.config import RAW_DIR
from pep_reign.transform.football_data_names import to_canonical

URL = "https://www.football-data.co.uk/mmz4281/{code}/E0.csv"

SOURCE_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "HS", "AS", "HST", "AST"]
RENAME = {
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",
}
COLUMNS = [
    "season",
    "date",
    "home",
    "away",
    "home_goals",
    "away_goals",
    "home_shots",
    "away_shots",
    "home_shots_on_target",
    "away_shots_on_target",
]


def season_code(season: str) -> str:
    """Convert '2016-17' to Football-Data's '1617' code."""
    start, end = season.split("-")
    return f"{start[-2:]}{end}"


def raw_path(season: str) -> Path:
    return RAW_DIR / "football-data" / f"E0_{season_code(season)}.csv"


def download_season(season: str, *, refresh: bool = False) -> Path:
    path = raw_path(season)
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = URL.format(code=season_code(season))
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    path.write_text(response.text, encoding="utf-8")
    return path


def parse(csv_text: str, season: str) -> pd.DataFrame:
    """Parse one season's CSV. Unplayed fixtures (no full-time score) are dropped."""
    raw = pd.read_csv(io.StringIO(csv_text))
    missing = [c for c in SOURCE_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"{season}: Football-Data file is missing columns {missing}")

    frame = raw[SOURCE_COLUMNS].dropna(subset=["FTHG", "FTAG"]).copy()
    frame["season"] = season
    frame["date"] = pd.to_datetime(frame["Date"], dayfirst=True, format="mixed")
    frame["home"] = frame["HomeTeam"].map(to_canonical)
    frame["away"] = frame["AwayTeam"].map(to_canonical)
    frame = frame.rename(columns=RENAME)

    count_columns = [c for c in RENAME.values()]
    frame[count_columns] = frame[count_columns].astype(int)
    return frame[COLUMNS].reset_index(drop=True)


def load_seasons(seasons: list[str], *, refresh: bool = False) -> pd.DataFrame:
    frames = []
    for season in seasons:
        path = download_season(season, refresh=refresh)
        frames.append(parse(path.read_text(encoding="utf-8"), season))
    return pd.concat(frames, ignore_index=True)
