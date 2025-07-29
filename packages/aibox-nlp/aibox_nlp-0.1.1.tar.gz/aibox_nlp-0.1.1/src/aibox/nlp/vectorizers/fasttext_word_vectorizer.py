"""Vetorizador de palavras baseado nos modelos do Fasttext."""

import re

import fasttext
import numpy as np

from aibox.nlp import resources
from aibox.nlp.core import Vectorizer


class FasttextWordVectorizer(Vectorizer):
    """Vetorização a nível de palavra baseada no FastText.

    :param language: linguagem do modelo.
    :param dims: dimensões do embedding.

    São utilizados os modelos pré-treinados do FastText. Atualmente,
    apenas a linguagem "pt" com 50 dimensões é suportada.

    O processo de vetorização ocorre da seguinte forma:
        1. Limpeza de múltiplos de caracteres de espaço (\s+) por um único;
        2. Tokenização através do método :py:meth:`str.split`;
        3. Para cada token, obtemos a representação dessa palavra;

    .. code-block:: python

        from aibox.nlp.vectorizers.fasttext_word_vectorizer import FasttextWordVectorizer

        # Instanciando
        vectorizer = FasttextWordVectorizer()
        text = "Esse é um texto de exemplo"

        # Obtendo os vetores para cada palavra do texto.
        vectorizer.vectorize(text).shape
        # Out: (6, 50)
    """

    def __init__(self, language: str = "pt", dims: int = 50):
        """Construtor de um word2vec
        utilizando os modelos pré-treinados
        do FastText.

        Args:

        """
        assert language in {"pt"}
        assert dims in {50}

        # Obtendo caminho para o modelo
        root = resources.path("embeddings/fasttext-cc-50.v1")
        model_path = root.joinpath("cc.pt.50.bin").absolute()

        # Carregando o modelo
        self._ft = fasttext.load_model(str(model_path))

    def _vectorize(self, text: str):
        words = self._tokenize(text)
        word_vectors = [self._ft.get_word_vector(w) for w in words]
        return np.array(word_vectors)

    def _tokenize(self, text: str) -> list[str]:
        return re.sub(r"\s+", " ", text).split()
