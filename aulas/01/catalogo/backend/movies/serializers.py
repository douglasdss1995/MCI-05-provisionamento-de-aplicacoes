"""
Serializers da aplicação de filmes.

O serializer é responsável por duas coisas:
1. Converter um objeto Python (Movie) em JSON para enviar ao frontend
2. Converter JSON recebido do frontend em dados validados para salvar no banco

Pense no serializer como um "tradutor" entre o banco de dados e a API.
"""

from rest_framework import serializers

from movies.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer completo do filme — usado para listagem e criação.

    Attributes:
        id: Identificador único (somente leitura).
        title: Título do filme.
        genre: Gênero do filme.
        year: Ano de lançamento.
        rating: Nota do filme (0.0 a 10.0).
        created_at: Data de cadastro (somente leitura).
    """

    class Meta:
        model = Movie
        fields = ["id", "title", "genre", "year", "rating", "created_at"]
        # Campos que o usuário não pode enviar — são preenchidos automaticamente
        read_only_fields = ["id", "created_at"]


class MovieRatingSerializer(serializers.Serializer):
    """Serializer usado apenas para atualizar a nota de um filme.

    Mantemos um serializer separado para garantir que apenas a nota
    pode ser alterada nesta operação — o título, gênero e ano não mudam.
    """

    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        min_value=0.0,
        max_value=10.0,
    )
