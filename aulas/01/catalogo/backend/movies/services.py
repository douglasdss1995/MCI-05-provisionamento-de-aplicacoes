"""
Services da aplicação de filmes.

Services contêm a lógica de negócio.
A view recebe a requisição HTTP e delega o trabalho real para o service.

Por que separar a lógica em services?
- A view fica fina: só trata HTTP (recebe, valida formato, retorna resposta)
- O service trata o negócio: validações, regras, efeitos colaterais
- Você pode reutilizar o service em outros contextos (tasks, CLI, etc.)
- Testes ficam mais simples: testa a regra sem montar uma requisição HTTP
"""

import structlog

from movies.exceptions import InvalidRating, MovieNotFound
from movies.models import Movie
from movies.selectors import get_movie_by_id

logger = structlog.get_logger(__name__)


def create_movie(title: str, genre: str, year: int, rating: float) -> Movie:
    """Cria um novo filme no banco de dados.

    Args:
        title: Título do filme.
        genre: Gênero do filme.
        year: Ano de lançamento.
        rating: Nota do filme (0.0 a 10.0).

    Returns:
        Instância do filme criado.

    Raises:
        InvalidRating: Se a nota estiver fora do intervalo permitido.
    """
    # Valida a nota antes de salvar no banco
    if not (0.0 <= float(rating) <= 10.0):
        raise InvalidRating()

    movie = Movie.objects.create(
        title=title,
        genre=genre,
        year=year,
        rating=rating,
    )

    logger.info("movie_created", movie_id=movie.pk, title=movie.title)
    return movie


def update_movie_rating(movie_id: int, rating: float) -> Movie:
    """Atualiza a nota de um filme existente.

    Args:
        movie_id: ID do filme a ser atualizado.
        rating: Nova nota (0.0 a 10.0).

    Returns:
        Instância do filme com a nota atualizada.

    Raises:
        MovieNotFound: Se o filme não existir.
        InvalidRating: Se a nova nota estiver fora do intervalo.
    """
    if not (0.0 <= float(rating) <= 10.0):
        raise InvalidRating()

    try:
        movie = get_movie_by_id(movie_id)
    except Movie.DoesNotExist:
        raise MovieNotFound()

    movie.rating = rating
    movie.save(update_fields=["rating"])

    logger.info("movie_rating_updated", movie_id=movie.pk, new_rating=rating)
    return movie


def delete_movie(movie_id: int) -> None:
    """Remove um filme do banco de dados.

    Args:
        movie_id: ID do filme a ser removido.

    Raises:
        MovieNotFound: Se o filme não existir.
    """
    try:
        movie = get_movie_by_id(movie_id)
    except Movie.DoesNotExist:
        raise MovieNotFound()

    logger.info("movie_deleted", movie_id=movie.pk, title=movie.title)
    movie.delete()
