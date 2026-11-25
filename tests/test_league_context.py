import pandas as pd
import pytest

from pep_reign.transform.league_context import (
    add_era,
    add_league_context,
    add_points_per_game,
    era_summary,
)


def _table() -> pd.DataFrame:
    # Two seasons, three teams each. Values are invented to test the arithmetic.
    return pd.DataFrame(
        {
            "season": ["2015-16"] * 3 + ["2016-17"] * 3,
            "team": ["A", "B", "C"] * 2,
            "played": [38] * 6,
            "points": [60, 50, 40, 90, 70, 50],
            "shots_for_per_game": [10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
            "shots_against_per_game": [11.0, 12.0, 13.0, 9.0, 10.0, 11.0],
            "shots_on_target_for_per_game": [4.0, 5.0, 6.0, 6.0, 7.0, 8.0],
        }
    )


def test_points_per_game() -> None:
    frame = add_points_per_game(_table())
    assert frame.loc[0, "points_per_game"] == pytest.approx(60 / 38)


def test_league_average_and_gap_per_season() -> None:
    frame = add_league_context(add_points_per_game(_table()))
    first = frame[frame["season"] == "2015-16"].set_index("team")
    assert first.loc["B", "shots_for_per_game_league_avg"] == pytest.approx(12.0)
    assert first.loc["A", "shots_for_per_game_vs_league"] == pytest.approx(-2.0)


def test_rank_is_within_season_with_1_as_highest() -> None:
    frame = add_league_context(add_points_per_game(_table()))
    second = frame[frame["season"] == "2016-17"].set_index("team")
    assert second.loc["C", "shots_for_per_game_rank"] == 1
    assert second.loc["A", "shots_for_per_game_rank"] == 3


def test_era_labels() -> None:
    frame = add_era(_table())
    assert set(frame.loc[frame["season"] == "2015-16", "era"]) == {"baseline"}
    assert set(frame.loc[frame["season"] == "2016-17", "era"]) == {"pep"}


def test_era_summary_averages_by_era() -> None:
    frame = add_era(add_league_context(add_points_per_game(_table())))
    summary = era_summary(frame[frame["team"] == "A"]).set_index("era")
    assert summary.loc["pep", "points_per_game"] == pytest.approx(90 / 38)
