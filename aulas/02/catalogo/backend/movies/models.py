"""
Model do Catálogo de Filmes.

O model é a representação de uma tabela no banco de dados.
Cada atributo da classe corresponde a uma coluna na tabela.
"""

from django.db import models


class Movie(models.Model):
    """Representa um filme no catálogo.

    Attributes:
        title: Título do filme.
        genre: Gênero do filme (ex: Ação, Drama, Comédia).
        year: Ano de lançamento.
        rating: Nota do filme de 0.0 a 10.0.
        created_at: Data e hora de cadastro, preenchida automaticamente.
    """

    title = models.CharField(max_length=200, verbose_name="Título")
    genre = models.CharField(max_length=100, verbose_name="Gênero")
    year = models.IntegerField(verbose_name="Ano")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name="Nota",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")

    class Meta:
        # Nome da tabela no banco de dados
        db_table = "movies"
        # Ordenação padrão: mais recentes primeiro
        ordering = ["-created_at"]
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"

    def __str__(self) -> str:
        """Representação textual do filme — usada no Django Admin."""
        return f"{self.title} ({self.year})"
