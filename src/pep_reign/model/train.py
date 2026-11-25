"""Train and evaluate a match-result model on a time-ordered split.

Question: does recent shot form predict match results better than the base rate?
The benchmark is a model that ignores form and predicts the training-set frequencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler

from pep_reign.model.features import FEATURE_COLUMNS, build_features

TEST_FROM = "2022-23"  # seasons from here on are held out; earlier seasons train the model


@dataclass(frozen=True)
class Report:
    test_from: str
    n_train: int
    n_test: int
    model_log_loss: float
    baseline_log_loss: float
    model_accuracy: float
    baseline_accuracy: float

    def as_dict(self) -> dict[str, float | int | str]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in asdict(self).items()}


def split(frame: pd.DataFrame, test_from: str = TEST_FROM) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Seasons are 'YYYY-YY', so string order matches time order."""
    train = frame[frame["season"] < test_from]
    test = frame[frame["season"] >= test_from]
    if train.empty or test.empty:
        raise ValueError(f"split at {test_from} leaves an empty train or test set")
    return train, test


def fit_model(train: pd.DataFrame) -> Pipeline:
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(train[FEATURE_COLUMNS], train["outcome"])
    return model


def evaluate(matches: pd.DataFrame, test_from: str = TEST_FROM) -> tuple[Report, Pipeline]:
    """Fit on seasons before `test_from`, score on the rest, and compare with the base rate."""
    frame = build_features(matches.reset_index(drop=True))
    train, test = split(frame, test_from)

    model = fit_model(train)
    classes = list(model.classes_)
    proba = model.predict_proba(test[FEATURE_COLUMNS])
    predicted = np.array(classes)[proba.argmax(axis=1)]

    base_rate = train["outcome"].value_counts(normalize=True).reindex(classes).to_numpy()
    baseline_proba = np.tile(base_rate, (len(test), 1))
    most_common = train["outcome"].value_counts().idxmax()

    report = Report(
        test_from=test_from,
        n_train=len(train),
        n_test=len(test),
        model_log_loss=log_loss(test["outcome"], proba, labels=classes),
        baseline_log_loss=log_loss(test["outcome"], baseline_proba, labels=classes),
        model_accuracy=accuracy_score(test["outcome"], predicted),
        baseline_accuracy=accuracy_score(test["outcome"], [most_common] * len(test)),
    )
    return report, model
