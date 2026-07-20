"""
URLs raiz do projeto.

Aqui registramos os prefixos de cada aplicação.
As rotas específicas de cada recurso ficam em seus próprios arquivos urls.py.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Painel de administração do Django — acessível em /admin/
    path("admin/", admin.site.urls),
    # Rotas da API de filmes — acessíveis em /api/movies/
    path("api/", include("movies.urls")),
]
