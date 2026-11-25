"""Download and parse Premier League results from openfootball (public domain).

Two text layouts appear across seasons:
  * "Home  2-1 (1-0)  Away"       (older seasons)
  * "Home v Away  2-1 (1-0)"      (newer seasons)
Both are handled here. Unplayed fixtures have no score and are skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx
import pandas as pd

from pep_reign.config import OPENFOOTBALL_URL, RAW_DIR
from pep_reign.transform.team_names import canonical

# A score sits between two runs of at least two spaces, with an optional half-time score.
_SCORE = re.compile(r"\s{2,}(\d+)-(\d+)(?:\s+\(\d+-\d+\))?(?=\s{2,}|\s*$)")
_KICKOFF = re.compile(r"^\s*\d{1,2}:\d{2}\s+")
_VS = re.compile(r"\s+v\s+")
_SKIP_PREFIXES = ("=", "#", "▪")

COLUMNS = ["season", "home", "away", "home_goals", "away_goals"]


def parse_line(line: str) -> tuple[str, str, int, int] | None:
    """Parse one fixture line into (home, away, home_goals, away_goals).

    Returns None for headers, dates, blank lines and unplayed fixtures.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith(_SKIP_PREFIXES):
        return None
    match = _SCORE.search(line)
    if match is None:
        return None

    left = _KICKOFF.sub("", line[: match.start()]).strip()
    right = line[match.end() :].strip()
    if _VS.search(left):
        left, right = (part.strip() for part in _VS.split(left, maxsplit=1))

    return canonical(left), canonical(right), int(match.group(1)), int(match.group(2))


def parse_text(text: str, season: str) -> pd.DataFrame:
    """Parse a full openfootball season file into a tidy DataFrame."""
    records = []
    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed is not None:
            home, away, hg, ag = parsed
            records.append((season, home, away, hg, ag))
    return pd.DataFrame(records, columns=COLUMNS)


def raw_path(season: str) -> Path:
    return RAW_DIR / "openfootball" / f"eng1_{season}.txt"


def download_season(season: str, *, refresh: bool = False) -> Path:
    """Fetch one season file into data/raw, reusing the cached copy unless refresh=True."""
    path = raw_path(season)
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    response = httpx.get(OPENFOOTBALL_URL.format(season=season), follow_redirects=True, timeout=30)
    response.raise_for_status()
    path.write_text(response.text, encoding="utf-8")
    return path


def load_seasons(seasons: list[str], *, refresh: bool = False) -> pd.DataFrame:
    """Download (if needed) and parse several seasons into one DataFrame."""
    frames = []
    for season in seasons:
        path = download_season(season, refresh=refresh)
        frames.append(parse_text(path.read_text(encoding="utf-8"), season))
    return pd.concat(frames, ignore_index=True)
