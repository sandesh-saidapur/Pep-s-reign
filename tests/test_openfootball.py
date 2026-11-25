from pathlib import Path

import pytest

from pep_reign.ingest.openfootball import parse_line, parse_text

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # older layout: home, score, away
        (
            "  12:30  Hull City                2-1 (1-0)  Leicester City",
            ("Hull City", "Leicester City", 2, 1),
        ),
        # newer layout: home v away, then score
        (
            "    20:00  Brighton & Hove Albion FC v Liverpool FC             3-2 (1-2)",
            ("Brighton & Hove Albion", "Liverpool", 3, 2),
        ),
    ],
)
def test_parses_both_layouts(line: str, expected: tuple) -> None:
    assert parse_line(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "= English Premier League 2016/17",
        "# Matches    380",
        "▪ Matchday 1",
        "  Sat Aug 13",
        "  15:00  Burnley FC               v Swansea City",  # unplayed: no score
    ],
)
def test_skips_non_results(line: str) -> None:
    assert parse_line(line) is None


def test_fixture_file_parses_every_result() -> None:
    text = (FIXTURES / "eng1_2016-17_head.txt").read_text(encoding="utf-8")
    frame = parse_text(text, "2016-17")
    assert len(frame) > 0
    assert frame["home_goals"].ge(0).all()
    assert set(frame["season"]) == {"2016-17"}
    assert not frame["home"].str.endswith(" FC").any()


def test_newer_layout_fixture_has_no_vs_in_team_names() -> None:
    text = (FIXTURES / "eng1_2024-25_tail.txt").read_text(encoding="utf-8")
    frame = parse_text(text, "2024-25")
    assert len(frame) > 0
    assert not frame["home"].str.contains(" v ").any()
    assert not frame["away"].str.contains(" v ").any()
