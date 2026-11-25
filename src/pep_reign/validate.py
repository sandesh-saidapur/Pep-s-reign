"""Schema checks for the data the pipeline produces.

Run these at every stage boundary, so bad input fails loudly, not silently.
"""

import pandera.pandas as pa

MATCH_SCHEMA = pa.DataFrameSchema(
    {
        "season": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}$")),
        "home": pa.Column(str, pa.Check.str_length(min_value=2)),
        "away": pa.Column(str, pa.Check.str_length(min_value=2)),
        "home_goals": pa.Column(int, pa.Check.ge(0)),
        "away_goals": pa.Column(int, pa.Check.ge(0)),
    },
    checks=[
        pa.Check(lambda df: df["home"] != df["away"], error="team plays itself"),
    ],
    strict=True,
)


def check_matches_complete(matches, expected_per_season: int = 380) -> None:
    """Every season should have a full league schedule: 20 clubs, 38 matchdays."""
    counts = matches.groupby("season").size()
    short = counts[counts != expected_per_season]
    if not short.empty:
        raise ValueError(f"incomplete seasons (expected {expected_per_season}): {short.to_dict()}")
