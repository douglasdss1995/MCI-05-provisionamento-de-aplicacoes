# Dockerfile do backend Django - Lista de Tarefas
# Imagem base leve, apenas com o necessario para rodar Python
FROM python:3.12-slim

# Evita arquivos .pyc e forca a saida dos logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copia o binario do uv de uma imagem oficial, sem precisar instalar via pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copia apenas os arquivos de dependencia primeiro
# Isso aproveita o cache do Docker quando o codigo muda mas as dependencias nao
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Agora copia o restante do codigo da aplicacao
COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]