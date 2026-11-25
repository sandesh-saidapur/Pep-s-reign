import numpy as np
import pandas as pd
import pytest

from pep_reign.model.features import FEATURE_COLUMNS, build_features, rolling_form
from pep_reign.model.train import evaluate, split


def _history(n_rounds: int = 10) -> pd.DataFrame:
    """A small synthetic league: four teams playing each other in rotation.

    The results are invented, not real. They exist only to test the mechanics.
    """
    teams = ["Alpha", "Beta", "Gamma", "Delta"]
    pairs = [(h, a) for h in teams for a in teams if h != a]
    rows = []
    day = pd.Timestamp("2016-08-01")
    for r in range(n_rounds):
        for i, (home, away) in enumerate(pairs):
            hg = (r + i) % 3
            ag = (r * 2 + i) % 3
            rows.append(
                {
                    "season": "2016-17" if r < n_rounds // 2 else "2017-18",
                    "date": day + pd.Timedelta(days=r * 14 + i),
                    "home": home,
                    "away": away,
                    "home_goals": hg,
                    "away_goals": ag,
                    "home_shots": 10 + (r + i) % 5,
                    "away_shots": 8 + (r * i) % 6,
                    "home_shots_on_target": 3 + (r + i) % 3,
                    "away_shots_on_target": 2 + (r * i) % 3,
                }
            )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def test_form_uses_only_earlier_matches() -> None:
    """Changing a match's own result must not change its own pre-match form."""
    matches = _history()
    before = rolling_form(matches)

    changed = matches.copy()
    changed.loc[20, ["home_goals", "away_goals", "home_shots", "away_shots"]] = [9, 0, 40, 1]
    after = rolling_form(changed)

    own_rows = [(20, "home"), (20, "away")]
    pd.testing.assert_frame_equal(
        before.loc[own_rows],
        after.loc[own_rows],
        check_exact=False,
    )


def test_form_is_nan_until_enough_history() -> None:
    form = rolling_form(_history())
    first_match = form.xs(0, level="match_id")
    assert first_match.isna().all().all()


def test_build_features_drops_short_history_and_builds_diffs() -> None:
    frame = build_features(_history())
    assert len(frame) > 0
    assert frame[FEATURE_COLUMNS].notna().all().all()
    expected = frame["form_points_home"] - frame["form_points_away"]
    np.testing.assert_allclose(frame["form_points_diff"], expected)
    assert set(frame["outcome"]) <= {"H", "D", "A"}


def test_build_features_rejects_non_unique_index() -> None:
    matches = _history()
    matches.index = [0] * len(matches)
    with pytest.raises(ValueError, match="unique"):
        build_features(matches)


def test_split_is_time_ordered() -> None:
    frame = pd.DataFrame({"season": ["2015-16", "2016-17", "2017-18"], "outcome": ["H", "D", "A"]})
    train, test = split(frame, "2017-18")
    assert list(train["season"]) == ["2015-16", "2016-17"]
    assert list(test["season"]) == ["2017-18"]


def test_split_rejects_empty_side() -> None:
    frame = pd.DataFrame({"season": ["2015-16"], "outcome": ["H"]})
    with pytest.raises(ValueError, match="empty"):
        split(frame, "2030-31")


def test_evaluate_runs_end_to_end_on_synthetic_history() -> None:
    matches = _history(n_rounds=12)
    report, model = evaluate(matches, test_from="2017-18")
    assert report.n_train > 0 and report.n_test > 0
    assert 0 < report.model_accuracy <= 1
    assert report.model_log_loss > 0
    assert list(model.classes_) == sorted(model.classes_)
