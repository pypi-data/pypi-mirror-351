"""Testes do pacote features."""

import os

import pytest

from aibox.nlp.factory import available_extractors, get_dataset, get_extractor


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
@pytest.mark.parametrize(
    "text",
    [
        "Esse é um texto de exemplo.",
        "Exemplo com parágrafos.\nEsse é um outro parágrafo. Essa é mais uma sentença.\nEsse um outro parágrafo.",
        *get_dataset("essayBR", extended=False, target_competence="C1")
        .to_frame()
        .iloc[1:4]
        .text.tolist(),
        *get_dataset("narrativeEssaysBR", target_competence="cohesion")
        .to_frame()
        .iloc[8:12]
        .text.tolist(),
    ],
)
def test_extractors(text: str, extractor_cls: str):
    extractor = get_extractor(extractor_cls, _config_for_cls(extractor_cls))
    extractor.extract(text)
