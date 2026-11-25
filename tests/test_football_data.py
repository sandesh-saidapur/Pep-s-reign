"""Tests for the Football-Data pipeline.

The CSV below is SYNTHETIC. It follows Football-Data's column layout, but the
values are invented to exercise the code. Real data is only downloaded by
`pep-reign shots`, and is never committed.
"""

import pandas as pd
import pytest

from pep_reign.ingest.football_data import parse, season_code
from pep_reign.transform.football_data_names import to_canonical
from pep_reign.transform.reconcile import check_scores_agree
from pep_reign.transform.shots import add_per_game_shots, shot_totals

SYNTHETIC_CSV = """Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HS,AS,HST,AST
E0,19/08/2017,12:30,Man City,Chelsea,2,0,H,15,8,7,3
E0,19/08/2017,15:00,Arsenal,Man United,1,1,D,10,12,4,5
E0,20/08/2017,15:00,Tottenham,Wolves,,,,,,,
"""


def test_season_code() -> None:
    assert season_code("2016-17") == "1617"
    assert season_code("2024-25") == "2425"


def test_parse_maps_names_drops_unplayed_and_types_counts() -> None:
    frame = parse(SYNTHETIC_CSV, "2017-18")
    assert len(frame) == 2  # the unplayed fixture is dropped
    assert frame.loc[0, "home"] == "Manchester City"
    assert frame.loc[0, "away"] == "Chelsea"
    assert frame.loc[0, "home_shots_on_target"] == 7
    assert frame["home_goals"].dtype.kind == "i"
    assert frame.loc[0, "date"] == pd.Timestamp("2017-08-19")


def test_parse_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing columns"):
        parse("Div,Date\nE0,19/08/2017\n", "2017-18")


def test_unmapped_team_name_fails_loudly() -> None:
    with pytest.raises(KeyError, match="unmapped"):
        to_canonical("Manchester Ciity")


def test_shot_totals_are_symmetric() -> None:
    frame = parse(SYNTHETIC_CSV, "2017-18")
    totals = shot_totals(frame).set_index("team")
    city = totals.loc["Manchester City"]
    assert city["shots_for"] == 15
    assert city["shots_against"] == 8
    assert city["shots_on_target_for"] == 7
    assert totals.loc["Chelsea", "shots_for"] == 8


def test_per_game_rates_join_to_table() -> None:
    frame = parse(SYNTHETIC_CSV, "2017-18")
    table = pd.DataFrame(
        {
            "season": ["2017-18", "2017-18", "2017-18", "2017-18"],
            "team": ["Manchester City", "Chelsea", "Arsenal", "Manchester United"],
            "played": [1, 1, 1, 1],
        }
    )
    merged = add_per_game_shots(table, shot_totals(frame)).set_index("team")
    assert merged.loc["Manchester City", "shots_for_per_game"] == 15


def test_per_game_join_refuses_missing_team() -> None:
    frame = parse(SYNTHETIC_CSV, "2017-18")
    table = pd.DataFrame({"season": ["2017-18"], "team": ["Burnley"], "played": [1]})
    with pytest.raises(ValueError, match="no shot data"):
        add_per_game_shots(table, shot_totals(frame))


def test_reconcile_passes_when_scores_agree() -> None:
    primary = pd.DataFrame(
        {
            "season": ["2017-18"],
            "home": ["Manchester City"],
            "away": ["Chelsea"],
            "home_goals": [2],
            "away_goals": [0],
        }
    )
    secondary = parse(SYNTHETIC_CSV, "2017-18")[
        ["season", "home", "away", "home_goals", "away_goals"]
    ].head(1)
    joined = check_scores_agree(primary, secondary)
    assert len(joined) == 1


def test_reconcile_fails_on_score_mismatch() -> None:
    primary = pd.DataFrame(
        {
            "season": ["2017-18"],
            "home": ["Manchester City"],
            "away": ["Chelsea"],
            "home_goals": [3],
            "away_goals": [0],
        }
    )
    secondary = parse(SYNTHETIC_CSV, "2017-18")[
        ["season", "home", "away", "home_goals", "away_goals"]
    ].head(1)
    with pytest.raises(ValueError, match="disagree on score"):
        check_scores_agree(primary, secondary)
