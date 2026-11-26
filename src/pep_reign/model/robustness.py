"""Repeat the match-result evaluation season by season, with bootstrap confidence intervals.

Each test season is scored by a model trained only on the seasons before it (expanding
window). Per-match log losses are then pooled, and a bootstrap over matches gives a
95% interval for the gap between the model and each benchmark.

Log loss: lower is better. Model minus bookmaker > 0 means the bookmaker was better.
Model minus base rate < 0 means the model was better than knowing nothing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pep_reign.model.features import FEATURE_COLUMNS, ODDS_COLUMNS, build_features
from pep_reign.model.train import fit_model, implied_probabilities

TEST_SEASONS = [
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]


def per_match_losses(matches: pd.DataFrame, test_seasons: list[str] = TEST_SEASONS) -> pd.DataFrame:
    """One row per scored match: the loss each predictor gave it."""
    frame = build_features(matches.reset_index(drop=True))
    rows = []
    for season in test_seasons:
        train = frame[frame["season"] < season]
        test = frame[frame["season"] == season]
        if train.empty or test.empty:
            raise ValueError(f"fold {season} has an empty train or test set")

        model = fit_model(train)
        classes = list(model.classes_)
        index = {c: i for i, c in enumerate(classes)}
        truth = test["outcome"].map(index).to_numpy()
        rows_idx = np.arange(len(test))

        proba = model.predict_proba(test[FEATURE_COLUMNS])
        base_rate = train["outcome"].value_counts(normalize=True).reindex(classes).to_numpy()

        priced = test[ODDS_COLUMNS].notna().all(axis=1).to_numpy()
        book_loss = np.full(len(test), np.nan)
        if priced.any():
            book = implied_probabilities(test[priced], classes)
            book_loss[priced] = -np.log(book[np.arange(priced.sum()), truth[priced]])

        rows.append(
            pd.DataFrame(
                {
                    "season": season,
                    "outcome": test["outcome"].to_numpy(),
                    "loss_model": -np.log(proba[rows_idx, truth]),
                    "loss_base": -np.log(base_rate[truth]),
                    "loss_book": book_loss,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def _bootstrap_mean_ci(
    values: np.ndarray, *, n_boot: int = 5000, seed: int = 0
) -> tuple[float, float, float]:
    """Mean and 95% percentile interval, resampling matches with replacement."""
    rng = np.random.default_rng(seed)
    n = len(values)
    samples = rng.integers(0, n, size=(n_boot, n))
    means = values[samples].mean(axis=1)
    return float(values.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarise(per_match: pd.DataFrame, *, n_boot: int = 5000, seed: int = 0) -> dict[str, object]:
    """Pooled log losses, the two gaps with confidence intervals, and the per-season table."""
    priced = per_match.dropna(subset=["loss_book"])

    gap_book = _bootstrap_mean_ci(
        (priced["loss_model"] - priced["loss_book"]).to_numpy(), n_boot=n_boot, seed=seed
    )
    gap_base = _bootstrap_mean_ci(
        (per_match["loss_model"] - per_match["loss_base"]).to_numpy(), n_boot=n_boot, seed=seed
    )
    return {
        "n_matches": int(len(per_match)),
        "n_matches_with_odds": int(len(priced)),
        "seasons": sorted(per_match["season"].unique().tolist()),
        "model_log_loss": round(float(per_match["loss_model"].mean()), 4),
        "base_rate_log_loss": round(float(per_match["loss_base"].mean()), 4),
        "bookmaker_log_loss": round(float(priced["loss_book"].mean()), 4),
        "model_minus_bookmaker": round(gap_book[0], 4),
        "model_minus_bookmaker_ci95": [round(gap_book[1], 4), round(gap_book[2], 4)],
        "model_minus_base_rate": round(gap_base[0], 4),
        "model_minus_base_rate_ci95": [round(gap_base[1], 4), round(gap_base[2], 4)],
    }


def by_season(per_match: pd.DataFrame) -> pd.DataFrame:
    """Mean log loss per season for each predictor, with the model's gap to each benchmark."""
    table = (
        per_match.groupby("season")[["loss_model", "loss_base", "loss_book"]].mean().reset_index()
    )
    table["model_minus_bookmaker"] = table["loss_model"] - table["loss_book"]
    table["model_minus_base_rate"] = table["loss_model"] - table["loss_base"]
    return table.round(4)
