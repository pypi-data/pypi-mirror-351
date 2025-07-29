"""Testes do pacote vectorizers."""

import pytest

from aibox.nlp.core import TrainableVectorizer
from aibox.nlp.factory import available_vectorizers, get_vectorizer


@pytest.mark.parametrize("vectorizer_cls", available_vectorizers())
def test_vectorizer(vectorizer_cls: str):
    # Get vectorizer
    vectorizer = get_vectorizer(vectorizer_cls)

    # Maybe it's trainable?
    if isinstance(vectorizer, TrainableVectorizer):
        vectorizer.fit(["Esse é um texto de treinamento."])

    for kind in ["numpy", "torch"]:
        vectorizer.vectorize("Esse é um texto de exemplo.", vector_type=kind)
