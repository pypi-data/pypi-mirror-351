"""Cacheamento na vetorização de textos."""

from abc import ABC, abstractmethod

import numpy as np

from aibox.nlp.core import TrainableVectorizer, Vectorizer
from aibox.nlp.typing import ArrayLike


class VectorizerCache(ABC):
    """Interface básica para um cacheador
    de vetorizador.
    """

    @abstractmethod
    def get(self, text: str) -> np.ndarray | None:
        """Obtém a representação numérica para
        esse texto caso exista no cache,
        ou retorna None.

        :param text: texto.

        :return: representação numérica ou None.
        """

    @abstractmethod
    def save(self, text: str, data: ArrayLike, overwrite: bool = False) -> bool:
        """Adiciona uma entrada no cache.

        :param text: texto.
        :param data: representação numérica.
        :param overwrite: se devemos sobrescrever caso
            o texto já esteja no cache.

        :return: indica se foi realizado o salvamento ou não.
        """

    def as_dict(self) -> dict[str, ArrayLike]:
        """Retorna esse cache como
        um dicionário de textos
        para NumPy arrays.

        :return: dicionário com os textos cacheados.
        """


class DictVectorizerCache(VectorizerCache):
    """Cache para vetorizadores.

    :param max_limit: quantidade máxima de entradas
        para armazenar. Se <= 0, não são aplicados limites.
    """

    def __init__(self, max_limit: int = -1):
        """Construtor."""
        self._max = max_limit
        self._cache: dict[str, ArrayLike] = dict()

    def get(self, text: str) -> np.ndarray | None:
        return self._cache.get(text, None)

    def save(self, text: str, data: np.ndarray, overwrite: bool = False) -> bool:
        if not overwrite and text in self._cache:
            return False

        self._cache[text] = data
        self._prune_to_limit()
        return True

    def as_dict(self) -> dict[str, np.ndarray]:
        return self._cache.copy()

    def _prune_to_limit(self):
        mem_size = len(self._cache)

        if self._max <= 0 or mem_size <= self._max:
            return

        keys = list(self._cache)
        diff = mem_size - self._max

        for k in keys[:diff]:
            del self._cache[k]


class CachedVectorizer(Vectorizer):
    """Vetorizador com memória auxiliar.

    :param vectorizer: vetorizador base.
    :param memory: memória auxiliar.

    Essa classe tenta primeiro obter uma entrada da memória,
    caso não exista, realiza a vetorização e salva no cache.
    """

    def __init__(self, vectorizer: Vectorizer, memory: VectorizerCache | None = None):
        self._vectorizer = vectorizer
        self._memory = memory

    @property
    def memory(self) -> VectorizerCache:
        return self._memory

    @property
    def vectorizer(self) -> Vectorizer:
        return self._vectorizer

    def _vectorize(self, text: str, **kwargs) -> ArrayLike:
        arr = self._memory.get(text)

        if arr is None:
            # Garantindo que não kwargs não contém
            #   chave duplicada
            kwargs.pop("vector_type", None)

            # Realizando vetorização
            arr = self._vectorizer.vectorize(text, vector_type="numpy", **kwargs)

            # Salvando na memória
            _ = self._memory.save(text, arr)

        return arr


class TrainableCachedVectorizer(TrainableVectorizer):
    """Vetorizador treinável com memória auxiliar.

    :param vectorizer: vetorizador base.
    :param memory: memória auxiliar.

    Essa classe tenta primeiro obter uma entrada da memória,
    caso não exista, realiza a vetorização e salva no cache.

    O processo de treinamento não é impactado pela presença
    do cache. Nenhuma vetorização de texto é salvo durante
    o processo de treinamento.
    """

    def __init__(
        self, vectorizer: TrainableVectorizer, memory: VectorizerCache | None = None
    ) -> None:
        self._cache = CachedVectorizer(vectorizer=vectorizer, memory=memory)
        self._trained = False

    @property
    def memory(self) -> VectorizerCache:
        return self._cache.memory

    @property
    def vectorizer(self) -> Vectorizer:
        return self._cache.vectorizer

    def fit(self, X: ArrayLike, y: None = None, **kwargs) -> None:
        if not self._trained:
            self._cache.vectorizer.fit(X, y, **kwargs)
            self._trained = True

    def _vectorize(self, text: str, **kwargs) -> ArrayLike:
        return self._cache._vectorize(text, **kwargs)
