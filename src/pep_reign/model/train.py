"""Train and evaluate a match-result model on a time-ordered split.

Two benchmarks:
  * the base rate: predict the training-set frequencies, ignoring everything else
  * bookmaker odds: Bet365 pre-match prices, with the overround removed. This is the
    strong benchmark. A model with no edge over it adds nothing.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from pep_reign.model.features import FEATURE_COLUMNS, ODDS_COLUMNS, build_features

TEST_FROM = "2022-23"  # seasons from here on are held out; earlier seasons train the model
ODDS_TO_CLASS = {"H": "home_odds", "D": "draw_odds", "A": "away_odds"}


@dataclass(frozen=True)
class Report:
    test_from: str
    n_train: int
    n_test: int
    model_log_loss: float
    baseline_log_loss: float
    model_accuracy: float
    baseline_accuracy: float
    # The odds comparison uses only test matches that have bookmaker prices.
    n_test_with_odds: int | None = None
    model_log_loss_odds_subset: float | None = None
    bookmaker_log_loss: float | None = None
    model_accuracy_odds_subset: float | None = None
    bookmaker_accuracy: float | None = None

    def as_dict(self) -> dict[str, float | int | str | None]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in asdict(self).items()}


def split(frame: pd.DataFrame, test_from: str = TEST_FROM) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Seasons are 'YYYY-YY', so string order matches time order."""
    train = frame[frame["season"] < test_from]
    test = frame[frame["season"] >= test_from]
    if train.empty or test.empty:
        raise ValueError(f"split at {test_from} leaves an empty train or test set")
    return train, test


def implied_probabilities(frame: pd.DataFrame, classes: list[str]) -> np.ndarray:
    """Bookmaker probabilities in `classes` order, with the overround removed."""
    raw = np.column_stack([1.0 / frame[ODDS_TO_CLASS[c]].to_numpy(dtype=float) for c in classes])
    return raw / raw.sum(axis=1, keepdims=True)


def fit_model(train: pd.DataFrame) -> Pipeline:
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(train[FEATURE_COLUMNS], train["outcome"])
    return model


def evaluate(matches: pd.DataFrame, test_from: str = TEST_FROM) -> tuple[Report, Pipeline]:
    """Fit on seasons before `test_from`, score on the rest, and compare with both benchmarks."""
    frame = build_features(matches.reset_index(drop=True))
    train, test = split(frame, test_from)

    model = fit_model(train)
    classes = list(model.classes_)
    proba = model.predict_proba(test[FEATURE_COLUMNS])
    predicted = np.array(classes)[proba.argmax(axis=1)]

    base_rate = train["outcome"].value_counts(normalize=True).reindex(classes).to_numpy()
    baseline_proba = np.tile(base_rate, (len(test), 1))
    most_common = train["outcome"].value_counts().idxmax()

    fields: dict[str, object] = {
        "test_from": test_from,
        "n_train": len(train),
        "n_test": len(test),
        "model_log_loss": log_loss(test["outcome"], proba, labels=classes),
        "baseline_log_loss": log_loss(test["outcome"], baseline_proba, labels=classes),
        "model_accuracy": accuracy_score(test["outcome"], predicted),
        "baseline_accuracy": accuracy_score(test["outcome"], [most_common] * len(test)),
    }

    if all(c in test.columns for c in ODDS_COLUMNS):
        priced = test[ODDS_COLUMNS].notna().all(axis=1).to_numpy()
        if priced.any():
            priced_test = test[priced]
            priced_proba = proba[priced]
            book = implied_probabilities(priced_test, classes)
            priced_predicted = predicted[priced]
            fields.update(
                {
                    "n_test_with_odds": int(priced.sum()),
                    "model_log_loss_odds_subset": log_loss(
                        priced_test["outcome"], priced_proba, labels=classes
                    ),
                    "bookmaker_log_loss": log_loss(priced_test["outcome"], book, labels=classes),
                    "model_accuracy_odds_subset": accuracy_score(
                        priced_test["outcome"], priced_predicted
                    ),
                    "bookmaker_accuracy": accuracy_score(
                        priced_test["outcome"], np.array(classes)[book.argmax(axis=1)]
                    ),
                }
            )

    return Report(**fields), model  # type: ignore[arg-type]
