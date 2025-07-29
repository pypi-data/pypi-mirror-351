"""Interface para vetorizadores."""

from abc import ABC, abstractmethod

import numpy as np
import torch

from aibox.nlp.typing import ArrayLike, TextArrayLike


class Vectorizer(ABC):
    """Interface para vetorizadores.

    Um vetorizador consegue converter textos (str)
    para uma representação numérica (vetor e/ou tensor).

    .. code-block:: python

        from aibox.nlp.core import Vectorizer

        # Exemplo de uso para classes concretas
        vectorizer = Vectorizer()
        text = "Esse é um texto de exemplo."

        # Realizando a vetorização
        vectorizer.vectorize(text, "numpy")
    """

    def vectorize(
        self, text: str, vector_type: str = "numpy", device: str | None = None, **kwargs
    ) -> np.ndarray | torch.Tensor:
        """Método para vetorização de um texto.

        :param text: texto de entrada.
        :param vector_type: tipo do vetor de saída ('numpy
            ou 'torch').
        :type vector_type: str, opcional
        :param device: dispositivo para armazenamento do tensor Torch. Padrão é
            CPU.
        :type device: str, opcional.
        :param `**kwargs`: parâmetros extras que podem ser utilizados
            por alguns vetorizadores para controlar o processo de
            vetorização.

        :return: representação numérica do texto.
        """
        # Obtendo representação vetorial
        text_vector = self._vectorize(text, **kwargs)
        is_np = isinstance(text_vector, np.ndarray)
        is_torch = isinstance(text_vector, torch.Tensor)

        if not is_np and not is_torch:
            # Por padrão, convertemos para NumPy
            text_vector = np.array(text_vector, dtype=np.float32)

        # Caso seja necessário um tensor, convertemos
        if (vector_type == "torch") and not is_torch:
            text_vector = torch.from_numpy(text_vector)

            if device is not None:
                text_vector = text_vector.to(device)

        # Caso seja necessário uma ndarray, convertemos
        if (vector_type == "numpy") and is_torch:
            text_vector = text_vector.numpy()

        return text_vector

    @abstractmethod
    def _vectorize(self, text: str, **kwargs) -> ArrayLike:
        """Método privado para vetorização do texto
        e retorno de um array-like qualquer (e.g., lista,
        tupla, ndarray, torch.Tensor, etc).

        :param text: texto que deve ser vetorizado.
        :param `**kwargs`: parâmetros extras que podem ser utilizados
            por alguns vetorizadores para controlar o processo de
            vetorização.

        :return: representação numérica do texto.
        """


class TrainableVectorizer(Vectorizer):
    """Representação de um vetorizador
    treinável (e.g., TF-IDF, BERT).

    Esse é um vetorizador que requer treinamento
    antes de ser utilizável diretamente. Apesar de
    possuir um método :py:meth:`fit`, não deve ser
    confundido com :py:class:`~aibox.nlp.core.estimator.Estimator`.

    O comportamento do método :py:meth:`vectorize` não é
    definido caso o vetorizador não tenha sido treinado.

    .. code-block:: python

        from aibox.nlp.core import TrainableVectorizer

        # Exemplo de uso para classes concretas
        vectorizer = TrainableVectorizer()
        train = ["Texto de treinamento 1.", "Texto de treinamento 2."]
        text = "Esse é um texto de exemplo."

        # Treinamento da classe
        vectorizer.fit(train)

        # Realizando a vetorização
        vectorizer.vectorize(text, "numpy")
    """

    def fit(self, X: TextArrayLike, y: None = None, **kwargs) -> None:
        """Método para treinamento do vetorizador. O valor de `y`
        não é utilizado, só é mantido por consistência da interface
        `fit(X, y)`.

        :param X: array-like de strings com formato (n_samples,).
        :param y: desconsiderado. Existe para compatibilidade com
            outras classes que implementam o método com mesmo nome.
        :param `**kwargs`: configurações extras que alguns vetorizadores
            treináveis podem utilizar.
        """
