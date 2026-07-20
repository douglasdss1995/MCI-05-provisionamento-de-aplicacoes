"""
Selectors da aplicação de filmes.

Selectors encapsulam as queries ao banco de dados.
As views nunca devem escrever queries diretamente — elas chamam selectors.

Por que separar queries em selectors?
- Queries ficam em um único lugar: fácil de encontrar e alterar
- A view não sabe como os dados são buscados — só recebe o resultado
- Facilita testes: você testa a query isolada da lógica HTTP
"""

from django.db.models import QuerySet

from movies.models import Movie


def get_all_movies(genre: str | None = None) -> QuerySet[Movie]:
    """Retorna todos os filmes, com filtro opcional por gênero.

    Args:
        genre: Se informado, filtra os filmes por este gênero.
               A busca é case-insensitive (ignora maiúsculas/minúsculas).

    Returns:
        QuerySet com os filmes encontrados, ordenados por data de cadastro.
    """
    queryset = Movie.objects.all()

    # Filtra por gênero apenas se o parâmetro foi informado
    if genre:
        queryset = queryset.filter(genre__icontains=genre)

    return queryset


def get_movie_by_id(movie_id: int) -> Movie:
    """Busca um filme pelo seu ID.

    Args:
        movie_id: ID do filme no banco de dados.

    Returns:
        Instância do filme encontrado.

    Raises:
        Movie.DoesNotExist: Se nenhum filme com este ID existir.
    """
    return Movie.objects.get(pk=movie_id)
