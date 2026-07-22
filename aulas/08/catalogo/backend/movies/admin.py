"""
Configuração do Django Admin para o modelo Movie.

O Admin é uma interface web gerada automaticamente pelo Django
para gerenciar os dados do banco sem precisar escrever código.
Acesse em: http://localhost:8000/admin/
"""

from django.contrib import admin

from movies.models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Configuração da tela de filmes no Admin."""

    # Colunas exibidas na listagem
    list_display = ["title", "genre", "year", "rating", "created_at"]

    # Filtros laterais
    list_filter = ["genre", "year"]

    # Campo de busca — busca por título e gênero
    search_fields = ["title", "genre"]

    # Ordenação padrão na listagem
    ordering = ["-created_at"]
