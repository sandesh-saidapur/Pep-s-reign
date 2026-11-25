"""Project-wide constants: paths, seasons and the club under study."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Pep Guardiola joined in summer 2016 and left after 2024/25.
FIRST_SEASON_START = 2016
LAST_SEASON_START = 2024
SEASONS: list[str] = [
    f"{y}-{str(y + 1)[-2:]}" for y in range(FIRST_SEASON_START, LAST_SEASON_START + 1)
]

CLUB = "Manchester City"

OPENFOOTBALL_URL = (
    "https://raw.githubusercontent.com/openfootball/england/master/{season}/1-premierleague.txt"
)
