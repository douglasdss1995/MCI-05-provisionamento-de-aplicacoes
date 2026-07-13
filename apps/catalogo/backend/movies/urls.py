"""
Roteamento de URLs da aplicação de filmes.

Cada URL mapeia um endereço para uma view específica.
Estas URLs são incluídas em core/urls.py com o prefixo /api/.

Resultado final:
  GET    /api/movies/            → lista e filtra filmes
  POST   /api/movies/            → cria um filme
  GET    /api/movies/<id>/       → detalhe de um filme
  DELETE /api/movies/<id>/       → remove um filme
  PATCH  /api/movies/<id>/rating/ → atualiza a nota
"""

from django.urls import path

from movies.views import MovieDetailView, MovieListView, MovieRatingView

urlpatterns = [
    # Rotas de coleção (operações sobre todos os filmes)
    path("movies/", MovieListView.as_view(), name="movie-list"),
    # Rotas de recurso (operações sobre um filme específico)
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),
    path("movies/<int:pk>/rating/", MovieRatingView.as_view(), name="movie-rating"),
]
