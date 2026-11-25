"""Streamlit view of Manchester City under Pep Guardiola, against the league and the baseline.

Run with:  make app   (after `pep-reign ingest`, `pep-reign shots`, `pep-reign tables`)
Needs the app extra:  uv sync --extra app
"""

from pathlib import Path

import pandas as pd
import streamlit as st

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

st.set_page_config(page_title="Pep's City", layout="wide")
st.title("Manchester City under Pep Guardiola")
st.caption(
    "Premier League, 2015/16 (pre-Pep baseline) to 2024/25. "
    "Shot counts are not chances; xG is not yet included."
)

seasons_path = PROCESSED / "city_seasons.csv"
era_path = PROCESSED / "city_era_summary.csv"
if not seasons_path.exists():
    st.warning(
        "No processed data yet. Run `pep-reign ingest`, `pep-reign shots` and `pep-reign tables`."
    )
    st.stop()

city = pd.read_csv(seasons_path)
era = pd.read_csv(era_path) if era_path.exists() else None

baseline = city[city["era"] == "baseline"]
pep = city[city["era"] == "pep"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pep seasons", len(pep))
col2.metric("Seasons finishing 1st", int((pep["position"] == 1).sum()))
col3.metric(
    "Points per game: Pep era",
    f"{pep['points_per_game'].mean():.2f}",
    delta=f"{pep['points_per_game'].mean() - baseline['points_per_game'].mean():+.2f} vs 2015/16",
)
if "shots_for_per_game_vs_league" in city.columns:
    col4.metric(
        "Shots for vs league: Pep era",
        f"{pep['shots_for_per_game_vs_league'].mean():+.2f} per game",
    )
else:
    col4.metric("Shots for vs league", "n/a")

st.subheader("Points per game by season")
st.bar_chart(city.set_index("season")["points_per_game"])

if "shots_for_per_game_vs_league" in city.columns:
    st.subheader("Shots per game against the league average")
    st.caption(
        "0 is the league average in each season. "
        "Higher shots-for and lower shots-against are better."
    )
    chart = city.set_index("season")[
        ["shots_for_per_game_vs_league", "shots_against_per_game_vs_league"]
    ].rename(
        columns={
            "shots_for_per_game_vs_league": "Shots for (vs league)",
            "shots_against_per_game_vs_league": "Shots against (vs league)",
        }
    )
    st.line_chart(chart)

    st.subheader("Rank in the league (1 = highest value)")
    rank_columns = {
        "shots_for_per_game_rank": "Shots for rank",
        "shots_against_per_game_rank": "Shots against rank (1 = most conceded)",
    }
    st.dataframe(
        city[["season", "era", *rank_columns]].rename(columns=rank_columns),
        hide_index=True,
        use_container_width=True,
    )

if era is not None:
    st.subheader("Baseline vs Pep era (averages)")
    st.dataframe(era, hide_index=True, use_container_width=True)

st.subheader("Season table")
st.dataframe(city, use_container_width=True, hide_index=True)
