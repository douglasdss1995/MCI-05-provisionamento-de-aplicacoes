# Aula 05 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-05-passo-a-passo-catalogo.md`.

## Antes de começar

Confirme que a stack da Aula 04 sobe corretamente:

```bash
docker compose up -d
docker compose ps
```

---

## Parte 1 — Criando o Arquivo .env

Na raiz do projeto, crie o arquivo `.env`:

```
POSTGRES_DB=todo
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=django-insecure-troque-esta-chave-em-producao
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Parte 2 — Atualizando o docker-compose.yml

Edite o `docker-compose.yml` para usar `env_file` em vez de variáveis inline:

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - todo-db-data:/var/lib/postgresql/data
    env_file:
      - .env
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres_user -d todo"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: sh -c "uv run python manage.py migrate && uv run gunicorn core.wsgi:application --bind 0.0.0.0:8000"
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "4200:80"

volumes:
  todo-db-data:
```

Reinicie a stack:

```bash
docker compose down
docker compose up -d --build
```

Confirme que tudo ainda funciona, acessando no navegador: `http://localhost:8000/api/tasks/`

---

## Parte 3 — Criando o .env.example

Crie o arquivo `.env.example` na raiz do projeto, documentando cada variável:

```
# .env.example
# Copie este arquivo para .env e preencha com valores reais antes de subir o projeto

# Configuracao do banco de dados PostgreSQL
POSTGRES_DB=todo
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Configuracao do Django
# Gere uma chave forte para producao, nunca reutilize a de desenvolvimento
SECRET_KEY=
# Em producao, DEBUG deve ser sempre False
DEBUG=True
# Lista de hosts permitidos, separados por virgula
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Parte 4 — Configurando o .gitignore

Crie ou edite o arquivo `.gitignore` na raiz do projeto:

```
.env
__pycache__/
*.pyc
node_modules/
dist/
.venv/
*.log
```

Confirme que o `.env` não aparece mais no `git status`:

```bash
git status
```

---

## Parte 5 — Configuração do Django com pydantic-settings

No arquivo `backend/core/settings.py` (ou arquivo de configuração equivalente do projeto), configure a leitura do `.env`:

```python
# core/settings.py
# Le as variaveis de ambiente do arquivo .env usando pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    """Define e valida todas as variaveis de ambiente do projeto."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Banco de dados PostgreSQL
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Django
    SECRET_KEY: str
    DEBUG: bool = False
    # Aceita uma string separada por virgulas: "localhost,127.0.0.1"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"


env = Env()

# ALLOWED_HOSTS chega como string — convertemos para lista aqui,
# porque o pydantic-settings nao faz esse parsing sozinho para list[str]
ALLOWED_HOSTS = [host.strip() for host in env.ALLOWED_HOSTS.split(",")]
```

> **Atenção:** os nomes das variáveis são em **maiúsculo** (`POSTGRES_DB`, `SECRET_KEY`, etc.) e precisam ser exatamente iguais aos usados no `.env` — é assim que o código real do projeto está estruturado. `ALLOWED_HOSTS` é lido como texto simples e convertido para lista manualmente com `.split(",")`; o `pydantic-settings` não faz esse parsing automático para campos `list[str]`.

---

## Parte 6 — Criando o .env de Produção

Crie um segundo arquivo, `.env.production`, para simular o ambiente de produção:

```
POSTGRES_DB=todo
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=uma-senha-bem-mais-forte-que-essa
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=uma-chave-secreta-diferente-e-forte-para-producao
DEBUG=False
ALLOWED_HOSTS=meusite.com.br
```

Este arquivo não será usado agora — é apenas para você visualizar a diferença entre os dois ambientes.

---

## Checklist final do dia

- [ ] `.env` criado e funcionando com o Compose
- [ ] `docker-compose.yml` atualizado para usar `env_file`
- [ ] `.env.example` documentado em português
- [ ] `.gitignore` configurado e `.env` fora do controle de versão
- [ ] Configuração Django lendo do `.env` via `pydantic-settings`
- [ ] `.env.production` criado como referência

---

## Material de apoio

- pydantic-settings — documentação oficial: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Docker Compose — env_file: https://docs.docker.com/reference/compose-file/services/#env_file
- GitHub — removendo dados sensíveis do repositório: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
