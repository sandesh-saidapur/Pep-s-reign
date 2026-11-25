import pandas as pd

from pep_reign.transform.tables import league_tables, team_season
from pep_reign.transform.team_names import canonical


def _matches() -> pd.DataFrame:
    # A tiny three-team league, played once each way (6 matches).
    rows = [
        ("2017-18", "Manchester City", "Chelsea", 2, 0),
        ("2017-18", "Chelsea", "Manchester City", 1, 1),
        ("2017-18", "Manchester City", "Arsenal", 3, 1),
        ("2017-18", "Arsenal", "Manchester City", 0, 0),
        ("2017-18", "Chelsea", "Arsenal", 2, 2),
        ("2017-18", "Arsenal", "Chelsea", 1, 0),
    ]
    return pd.DataFrame(rows, columns=["season", "home", "away", "home_goals", "away_goals"])


def test_points_and_goals_are_correct() -> None:
    table = league_tables(_matches()).set_index("team")
    city = table.loc["Manchester City"]
    # City: W vs Chelsea (2-0 at home), D at Chelsea (1-1), W vs Arsenal (3-1), D at Arsenal (0-0).
    assert city["points"] == 3 + 1 + 3 + 1
    assert city["goals_for"] == 2 + 1 + 3 + 0
    assert city["goals_against"] == 0 + 1 + 1 + 0
    assert city["played"] == 4


def test_positions_are_ordered_by_points() -> None:
    table = league_tables(_matches())
    assert table["position"].tolist() == [1, 2, 3]
    assert table.iloc[0]["points"] >= table.iloc[1]["points"] >= table.iloc[2]["points"]


def test_points_sum_matches_results() -> None:
    table = league_tables(_matches())
    # Three decisive results (3 points each) plus three draws (2 points between them).
    assert table["points"].sum() == 3 * 3 + 3 * 2
    assert table.set_index("team").loc["Manchester City", "points"] == 8


def test_team_season_returns_one_club() -> None:
    city = team_season(league_tables(_matches()), "Manchester City")
    assert list(city["team"].unique()) == ["Manchester City"]


def test_canonical_strips_fc_and_whitespace() -> None:
    assert canonical("Manchester City FC") == "Manchester City"
    assert canonical("  Chelsea   FC ") == "Chelsea"
    assert canonical("Brighton & Hove Albion") == "Brighton & Hove Albion"


def test_canonical_strips_afc_suffix_but_keeps_afc_prefix() -> None:
    assert canonical("Sunderland AFC") == "Sunderland"
    assert canonical("AFC Bournemouth") == "AFC Bournemouth"
