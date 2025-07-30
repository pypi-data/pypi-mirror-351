"""Testes do pacote vectorizers."""

import pytest

from aibox.nlp.core import TrainableVectorizer
from aibox.nlp.factory import available_vectorizers, get_vectorizer
from aibox.nlp.vectorizers.fasttext_word_vectorizer import (
    FTAggregationStrategy,
    FTTokenizerStrategy,
)


@pytest.mark.parametrize("vectorizer_cls", available_vectorizers())
def test_vectorizer(vectorizer_cls: str):
    # Get vectorizer
    vectorizer = get_vectorizer(vectorizer_cls)

    # Maybe it's trainable?
    if isinstance(vectorizer, TrainableVectorizer):
        vectorizer.fit(["Esse é um texto de treinamento."])

    for kind in ["numpy", "torch"]:
        vectorizer.vectorize("Esse é um texto de exemplo.", vector_type=kind)


@pytest.mark.parametrize("aggregation", FTAggregationStrategy)
@pytest.mark.parametrize("tokenizer", FTTokenizerStrategy)
def test_fasttext_vectorizer(
    aggregation: FTAggregationStrategy, tokenizer: FTTokenizerStrategy
):
    # Initialize vectorizer
    vectorizer = get_vectorizer(
        "fasttextWordVectorizer", aggregation=aggregation, tokenizer=tokenizer
    )

    # Vectorize text
    out = vectorizer.vectorize("Esse é um texto de exemplo.")

    # Assertions
    if aggregation == FTAggregationStrategy.NONE:
        assert len(out.shape) == 2
        assert out.shape[-1] == 50
    elif aggregation == FTAggregationStrategy.AVERAGE:
        assert out.shape == (50,)
