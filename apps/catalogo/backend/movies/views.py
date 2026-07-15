"""
Views da aplicação de filmes.

As views são orquestradores finos: recebem a requisição HTTP,
delegam o trabalho para services/selectors, e retornam a resposta.

A view NÃO deve conter lógica de negócio.
Se você se pegar escrevendo um if complexo na view, mova para um service.
"""

import structlog
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.exceptions import MovieNotFound
from movies.models import Movie
from movies.selectors import get_all_movies, get_movie_by_id
from movies.serializers import MovieRatingSerializer, MovieSerializer
from movies.services import create_movie, delete_movie, update_movie_rating

logger = structlog.get_logger(__name__)


class MovieListView(APIView):
    """Listagem e criação de filmes.

    GET  /api/movies/         → lista todos os filmes
    GET  /api/movies/?genre=X → filtra por gênero
    POST /api/movies/         → cria um novo filme
    """

    def get(self, request: Request) -> Response:
        """Lista os filmes, com filtro opcional por gênero."""
        # Lê o parâmetro de query string: /api/movies/?genre=Ação
        genre = request.query_params.get("genre")

        movies = get_all_movies(genre=genre)
        serializer = MovieSerializer(movies, many=True)

        logger.info("movies_listed", count=movies.count(), genre_filter=genre)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Cria um novo filme a partir dos dados enviados no corpo da requisição."""
        serializer = MovieSerializer(data=request.data)

        # Valida os dados recebidos — retorna 400 se algo estiver errado
        serializer.is_valid(raise_exception=True)

        # Delega a criação para o service
        movie = create_movie(**serializer.validated_data)

        return Response(MovieSerializer(movie).data, status=status.HTTP_201_CREATED)


class MovieDetailView(APIView):
    """Consulta, atualização de nota e remoção de um filme específico.

    GET    /api/movies/<id>/        → retorna um filme
    PATCH  /api/movies/<id>/rating/ → atualiza apenas a nota
    DELETE /api/movies/<id>/        → remove o filme
    """

    def _get_movie_or_404(self, movie_id: int) -> Movie:
        """Busca o filme ou lança 404 se não existir."""
        try:
            return get_movie_by_id(movie_id)
        except Movie.DoesNotExist:
            raise MovieNotFound()

    def get(self, request: Request, pk: int) -> Response:
        """Retorna os dados de um filme específico."""
        movie = self._get_movie_or_404(pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Remove um filme do catálogo."""
        delete_movie(pk)
        # 204 No Content: operação bem-sucedida, sem corpo na resposta
        return Response(status=status.HTTP_204_NO_CONTENT)


class MovieRatingView(APIView):
    """Atualização da nota de um filme.

    PATCH /api/movies/<id>/rating/ → atualiza apenas a nota
    """

    def patch(self, request: Request, pk: int) -> Response:
        """Atualiza a nota de um filme específico."""
        serializer = MovieRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie = update_movie_rating(pk, serializer.validated_data["rating"])
        return Response(MovieSerializer(movie).data)
