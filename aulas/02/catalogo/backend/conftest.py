"""
Configuração global do pytest.

Este arquivo é carregado automaticamente pelo pytest antes de qualquer teste.
Aqui definimos as variáveis de ambiente mínimas para que o Django funcione
durante os testes, sem depender de um arquivo .env no disco.
"""

import os

# Define as variáveis de ambiente para o banco de dados de teste.
# O pytest-django cria um banco separado chamado "test_<POSTGRES_DB>"
# para não interferir no banco de desenvolvimento.
os.environ.setdefault("POSTGRES_DB", "catalogo")
os.environ.setdefault("POSTGRES_USER", "postgres_user")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres_pass")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")

# Chave secreta usada apenas nos testes — nunca usar em produção
os.environ.setdefault("SECRET_KEY", "chave-secreta-apenas-para-testes-nao-usar-em-producao")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")
