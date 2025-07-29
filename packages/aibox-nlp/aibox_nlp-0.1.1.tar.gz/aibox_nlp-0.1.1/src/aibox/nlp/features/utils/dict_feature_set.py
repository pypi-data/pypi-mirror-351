"""Conjunto de características
como um :py:class:`dict`.
"""

from aibox.nlp.core import FeatureSet


class DictFeatureSet(FeatureSet):
    """Implementação de um
    :py:class:`~aibox.nlp.core.feature_extractor.FeatureSet`
    a partir de um dicionário arbitrário.
    """

    def __init__(self, data: dict[str, float]):
        self._d = data

    def as_dict(self) -> dict[str, float]:
        lexical_sorted_dict = dict(sorted(self._d.items(), key=lambda x: x[0]))
        return lexical_sorted_dict
