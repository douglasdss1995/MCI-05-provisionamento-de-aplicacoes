"""
Exceções customizadas da aplicação de filmes.

Centralizar as exceções aqui facilita o tratamento de erros nas views
e torna o código mais legível — você sabe exatamente o que pode dar errado.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class MovieNotFound(APIException):
    """Lançada quando um filme com o ID solicitado não existe no banco."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Filme não encontrado."
    default_code = "movie_not_found"


class InvalidRating(APIException):
    """Lançada quando a nota informada está fora do intervalo permitido (0.0 a 10.0)."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A nota deve ser um valor entre 0.0 e 10.0."
    default_code = "invalid_rating"
