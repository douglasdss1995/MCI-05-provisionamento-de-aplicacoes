#!/bin/sh
# entrypoint.sh
# Executa as tarefas de inicializacao antes de subir o servidor

set -e

echo "Coletando arquivos estaticos..."
uv run python manage.py collectstatic --noinput

echo "Aplicando migrations..."
uv run python manage.py migrate

echo "Iniciando o servidor..."
exec uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000