"""Cross-check two sources that report the same matches.

openfootball and Football-Data should agree on every score. A disagreement means a
name mapping, a date or a source error, so it stops the pipeline.
"""

from __future__ import annotations

import pandas as pd

KEY = ["season", "home", "away"]


def check_scores_agree(primary: pd.DataFrame, secondary: pd.DataFrame) -> pd.DataFrame:
    """Join on season and teams, then require identical full-time goals.

    Returns the joined frame. Raises ValueError on any score mismatch or on matches
    that appear in only one source.
    """
    joined = primary.merge(
        secondary,
        on=KEY,
        how="outer",
        suffixes=("_primary", "_secondary"),
        indicator=True,
    )
    only_one_side = joined[joined["_merge"] != "both"]
    if not only_one_side.empty:
        raise ValueError(f"{len(only_one_side)} matches present in only one source")

    both = joined[joined["_merge"] == "both"]
    mismatch = both[
        (both["home_goals_primary"] != both["home_goals_secondary"])
        | (both["away_goals_primary"] != both["away_goals_secondary"])
    ]
    if not mismatch.empty:
        first = mismatch.iloc[0]
        raise ValueError(
            f"{len(mismatch)} matches disagree on score; first: "
            f"{first['season']} {first['home']} v {first['away']}"
        )
    return both.drop(columns="_merge")
