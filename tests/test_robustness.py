import numpy as np
import pandas as pd
import pytest

from pep_reign.model.robustness import _bootstrap_mean_ci, by_season, per_match_losses, summarise
from tests.test_model import _history


def test_bootstrap_interval_brackets_the_mean() -> None:
    values = np.array([0.1, 0.4, 0.2, 0.9, 0.5, 0.3, 0.6, 0.2])
    mean, low, high = _bootstrap_mean_ci(values, n_boot=2000, seed=1)
    assert low <= mean <= high
    assert mean == pytest.approx(values.mean())


def test_bootstrap_of_identical_values_is_a_point() -> None:
    mean, low, high = _bootstrap_mean_ci(np.full(10, 0.7), n_boot=500, seed=0)
    assert (mean, low, high) == pytest.approx((0.7, 0.7, 0.7))


def test_per_match_losses_are_positive_and_cover_each_season() -> None:
    losses = per_match_losses(_history(n_rounds=12), test_seasons=["2017-18"])
    assert set(losses["season"]) == {"2017-18"}
    assert (losses[["loss_model", "loss_base"]] > 0).all().all()
    assert losses["loss_book"].notna().all()


def test_summary_and_by_season_are_consistent() -> None:
    losses = pd.DataFrame(
        {
            "season": ["2017-18"] * 4 + ["2018-19"] * 4,
            "outcome": ["H"] * 8,
            "loss_model": [0.9, 1.0, 0.8, 1.1, 0.9, 1.0, 0.8, 1.1],
            "loss_base": [1.1] * 8,
            "loss_book": [0.95] * 8,
        }
    )
    summary = summarise(losses, n_boot=500)
    interval = summary["model_minus_bookmaker_ci95"]
    assert isinstance(interval, list)
    low, high = float(interval[0]), float(interval[1])
    assert low <= float(summary["model_minus_bookmaker"]) <= high  # type: ignore[arg-type]
    assert summary["n_matches"] == 8

    table = by_season(losses).set_index("season")
    assert table.loc["2017-18", "loss_model"] == pytest.approx(0.95)
