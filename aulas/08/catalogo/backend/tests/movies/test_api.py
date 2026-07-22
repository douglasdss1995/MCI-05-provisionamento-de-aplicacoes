"""
Testes de integração da API de filmes.

Testes de integração testam o sistema completo: a requisição HTTP entra,
passa pela view, pelo service, chega ao banco de dados (de teste),
e verificamos a resposta final.

Usamos @pytest.mark.django_db para que o pytest crie um banco temporário
antes de cada teste e limpe tudo ao final.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie


@pytest.fixture
def api_client() -> APIClient:
    """Cliente HTTP para chamar a API nos testes."""
    return APIClient()


@pytest.fixture
def movie_payload() -> dict:
    """Dados válidos para criar um filme nos testes."""
    return {
        "title": "Inception",
        "genre": "Sci-Fi",
        "year": 2010,
        "rating": "8.8",
    }


@pytest.fixture
def created_movie(movie_payload: dict) -> Movie:
    """Cria um filme diretamente no banco para usar em outros testes."""
    return Movie.objects.create(**{**movie_payload, "rating": 8.8})


@pytest.mark.django_db
class TestMovieList:
    """Testes do endpoint GET/POST /api/movies/"""

    def test_list_returns_200_when_empty(self, api_client: APIClient) -> None:
        """Lista vazia deve retornar 200 com array vazio, não 404."""
        url = reverse("movie-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_list_returns_all_movies(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """Deve retornar todos os filmes cadastrados."""
        url = reverse("movie-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == created_movie.title

    def test_filter_by_genre(self, api_client: APIClient) -> None:
        """Filtro por gênero deve retornar apenas os filmes do gênero informado."""
        Movie.objects.create(title="Inception", genre="Sci-Fi", year=2010, rating=8.8)
        Movie.objects.create(title="The Godfather", genre="Drama", year=1972, rating=9.2)

        url = reverse("movie-list")
        response = api_client.get(url, {"genre": "Sci-Fi"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["genre"] == "Sci-Fi"

    def test_create_movie_returns_201(
        self, api_client: APIClient, movie_payload: dict
    ) -> None:
        """Criação bem-sucedida deve retornar 201 com os dados do filme criado."""
        url = reverse("movie-list")
        response = api_client.post(url, movie_payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == movie_payload["title"]
        assert response.data["id"] is not None

    def test_create_movie_persists_in_database(
        self, api_client: APIClient, movie_payload: dict
    ) -> None:
        """Após criação, o filme deve existir no banco de dados."""
        url = reverse("movie-list")
        api_client.post(url, movie_payload, format="json")

        assert Movie.objects.count() == 1
        assert Movie.objects.first().title == movie_payload["title"]

    def test_create_movie_with_invalid_rating_returns_400(
        self, api_client: APIClient
    ) -> None:
        """Nota acima de 10.0 deve ser rejeitada com erro 400."""
        url = reverse("movie-list")
        payload = {
            "title": "Teste",
            "genre": "Drama",
            "year": 2020,
            "rating": "11.0",  # inválido — máximo é 10.0
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_movie_missing_required_field_returns_400(
        self, api_client: APIClient
    ) -> None:
        """Requisição sem campo obrigatório (title) deve retornar 400."""
        url = reverse("movie-list")
        response = api_client.post(url, {"genre": "Drama"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMovieDetail:
    """Testes dos endpoints GET/DELETE /api/movies/<id>/"""

    def test_get_movie_returns_200(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """Busca por ID existente deve retornar 200 com os dados do filme."""
        url = reverse("movie-detail", kwargs={"pk": created_movie.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == created_movie.pk

    def test_get_nonexistent_movie_returns_404(self, api_client: APIClient) -> None:
        """Busca por ID inexistente deve retornar 404."""
        url = reverse("movie-detail", kwargs={"pk": 99999})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_movie_returns_204(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """Remoção bem-sucedida deve retornar 204 sem corpo."""
        url = reverse("movie-detail", kwargs={"pk": created_movie.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Movie.objects.count() == 0

    def test_delete_nonexistent_movie_returns_404(self, api_client: APIClient) -> None:
        """Tentar remover um filme inexistente deve retornar 404."""
        url = reverse("movie-detail", kwargs={"pk": 99999})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestMovieRating:
    """Testes do endpoint PATCH /api/movies/<id>/rating/"""

    def test_update_rating_returns_200(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """Atualização de nota válida deve retornar 200 com a nota atualizada."""
        url = reverse("movie-rating", kwargs={"pk": created_movie.pk})
        response = api_client.patch(url, {"rating": "9.5"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert float(response.data["rating"]) == 9.5

    def test_update_rating_persists_in_database(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """A nota atualizada deve ser salva no banco de dados."""
        url = reverse("movie-rating", kwargs={"pk": created_movie.pk})
        api_client.patch(url, {"rating": "7.0"}, format="json")

        created_movie.refresh_from_db()
        assert float(created_movie.rating) == 7.0

    def test_update_rating_above_max_returns_400(
        self, api_client: APIClient, created_movie: Movie
    ) -> None:
        """Nota acima de 10.0 deve ser rejeitada."""
        url = reverse("movie-rating", kwargs={"pk": created_movie.pk})
        response = api_client.patch(url, {"rating": "10.5"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_rating_for_nonexistent_movie_returns_404(
        self, api_client: APIClient
    ) -> None:
        """Atualizar nota de filme inexistente deve retornar 404."""
        url = reverse("movie-rating", kwargs={"pk": 99999})
        response = api_client.patch(url, {"rating": "8.0"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
