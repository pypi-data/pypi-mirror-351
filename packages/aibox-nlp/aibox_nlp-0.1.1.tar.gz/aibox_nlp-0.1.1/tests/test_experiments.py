"""Testes do pacote experiments."""

import numpy as np
import pandas as pd
import pytest

from aibox.nlp.core import Dataset, Estimator, Metric, Pipeline, Vectorizer
from aibox.nlp.experiments.simple_experiment import SimpleExperiment
from aibox.nlp.typing import ArrayLike


class DummyVectorizer(Vectorizer):
    def __init__(self, state: int):
        self.state = state

    def _vectorize(self, text: str, **kwargs) -> ArrayLike:
        return np.array([self.state], dtype=np.float32)


class DummyEstimator(Estimator):
    def __init__(self, random_state: int):
        super().__init__(random_state=random_state)

    def predict(self, X: ArrayLike, **kwargs) -> np.ndarray:
        return np.array([self.random_state], dtype=np.float32)

    def fit(self, X: ArrayLike, y: ArrayLike, **kwargs): ...

    @property
    def hyperparameters(self):
        return dict(seed=self.random_state)

    @property
    def params(self):
        return dict(state=self.random_state)


class DummyDataset(Dataset):
    def __init__(self, as_reg: bool):
        self._df = pd.DataFrame(
            dict(text=["Não utilizado.", "Não utilizado"], target=[0, 1])
        )

        if as_reg:
            self._df["target"] = self._df.target.astype(np.float32)

    def to_frame(self):
        return self._df

    def cv_splits(self, k: int, stratified: bool, seed: int) -> list[pd.DataFrame]: ...

    def train_test_split(
        self, frac_train: float, stratified: bool, seed: int
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        return self._df, self._df


class DummyMetric(Metric):
    def name(self) -> str:
        return "Dummy"

    def compute(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray[np.float32]:
        return np.array(0.0)


@pytest.mark.parametrize("is_reg", [True, False])
def test_simple_experiment(is_reg: bool):
    # Initialize experiment
    experiment = SimpleExperiment(
        pipelines=[
            Pipeline(DummyVectorizer(42), DummyEstimator(80), name="Pipeline 1"),
            Pipeline(DummyVectorizer(43), DummyEstimator(81), name="Pipeline 2"),
        ],
        dataset=DummyDataset(is_reg),
        metrics=[DummyMetric()],
        criteria_best=DummyMetric(),
        seed=8080,
    )

    # Run experiment
    result = experiment.run()

    # Assertions
    assert result.extras is not None
    assert np.allclose(result.best_metrics["Dummy"], 0.0)
    assert result.best_pipeline.name == "Pipeline 2"
