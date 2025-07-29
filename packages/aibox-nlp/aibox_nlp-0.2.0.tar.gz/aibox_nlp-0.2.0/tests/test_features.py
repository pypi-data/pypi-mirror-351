"""Testes do pacote features."""

import os
import pytest

from aibox.nlp.factory import available_extractors, get_extractor


def _config_for_cls(extractor_cls: str) -> dict:
    if extractor_cls in {
        "bertSimilarityBR",
        "fuzzySimilarity",
        "nilcSimilarityBR",
        "tfidfSimilarity",
    }:
        return dict(reference_text="Esse é o texto de referência.")

    return dict()


@pytest.mark.skipif(
    os.environ.get("TEST_EXPENSIVE_AIBOX_NLP", None) is None,
    reason="'TEST_EXPENSIVE_AIBOX_NLP' is unset.",
)
@pytest.mark.parametrize("extractor_cls", available_extractors())
def test_extractors(extractor_cls: str):
    extractor = get_extractor(extractor_cls, _config_for_cls(extractor_cls))
    extractor.extract("Esse é um texto de exemplo.")
