"""Streamlit view of Manchester City's season-by-season record.

Run with:  streamlit run dashboards/app.py   (after `pep-reign ingest` and `pep-reign tables`)
"""

from pathlib import Path

import pandas as pd
import streamlit as st

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

st.set_page_config(page_title="Pep's City", layout="wide")
st.title("Manchester City under Pep Guardiola")

path = PROCESSED / "city_seasons.csv"
if not path.exists():
    st.warning("No processed data yet. Run `pep-reign ingest` then `pep-reign tables`.")
    st.stop()

city = pd.read_csv(path)
city["points_per_game"] = city["points"] / city["played"]

col1, col2, col3 = st.columns(3)
col1.metric("Seasons", len(city))
col2.metric("Titles-level finishes (top 1)", int((city["position"] == 1).sum()))
col3.metric("Average points per game", f"{city['points_per_game'].mean():.2f}")

st.subheader("Points per game by season")
st.bar_chart(city.set_index("season")["points_per_game"])

st.subheader("Season table")
st.dataframe(city, use_container_width=True, hide_index=True)
