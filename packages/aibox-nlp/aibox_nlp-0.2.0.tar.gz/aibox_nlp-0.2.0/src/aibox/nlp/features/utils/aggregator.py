"""Agregação de características e extratores."""

from typing import Iterable

from aibox.nlp.core import FeatureExtractor, FeatureSet


class AggregatedFeatures(FeatureSet):
    """Conjunto de características agregadas.

    :param `*features`: conjuntos de características
        a serem agregados.

    Essa classe permite que características oriundas de múltiplos
    extratores sejam tratadas como sendo de um único extrator.
    """

    def __init__(self, *features: FeatureSet):
        self._features = features

    def as_dict(self) -> dict[str, float]:
        combined_dict = {k: v for fs in self._features for k, v in fs.as_dict().items()}
        sorted_dict = dict(sorted(combined_dict.items(), key=lambda x: x[0]))
        return sorted_dict

    @property
    def features_sets(self) -> Iterable[FeatureSet]:
        """Características base presentes
        no objeto.

        :return: características base.
        """
        return self._features


class AggregatedFeatureExtractor(FeatureExtractor):
    """Agregação de extratores de características.

    :param `*extractors`: extratores de características.
    """

    def __init__(self, *extractors) -> None:
        self._extractors = extractors

    @property
    def extractors(self) -> list[FeatureExtractor]:
        """Extratores presentes na agregação.

        :return: extratores.
        """
        return self._extractors

    def extract(self, text: str, **kwargs) -> AggregatedFeatures:
        del kwargs

        features = [e.extract(text) for e in self._extractors]
        return AggregatedFeatures(*features)
