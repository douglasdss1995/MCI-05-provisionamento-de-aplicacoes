# Aula 04 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-04-passo-a-passo-catalogo.md`.

## Antes de começar

Confirme que os Dockerfiles do backend e do frontend da Aula 02 estão salvos em suas respectivas pastas dentro do repositório.

---

## Parte 1 — Criando o docker-compose.yml

Na da pasta `apps/todo/`, crie o arquivo `docker-compose.yml`:

Antes de criar o `docker-compose.yml`, edite o `frontend/nginx.conf` da Aula 02. Ele
aponta o `proxy_pass` para `todo-backend` — o nome que demos ao container na
Aula 02 com `docker run --name todo-backend`. No Compose, o serviço se chama
apenas `backend` (é o nome usado abaixo, em `services:`), e é esse nome — não
`todo-backend` — que o DNS interno do Compose resolve. Troque a linha:

```nginx
proxy_pass http://todo-backend:8000;
```

por:

```nginx
proxy_pass http://backend:8000;
```

Sem essa troca, o Nginx do frontend não consegue resolver o host configurado
no `proxy_pass` e **recusa subir** (`nginx: [emerg] host not found in
upstream "todo-backend"`) — o container do frontend aparece com status
`Exited` em `docker compose ps`.

```yaml
# docker-compose.yml
# Orquestra os tres servicos da aplicacao Lista de Tarefas:
# banco de dados, backend Django e frontend Angular

services:
  db:
    image: postgres:16
    volumes:
      - todo-db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: todo
      POSTGRES_USER: postgres_user
      POSTGRES_PASSWORD: postgres_pass
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
    environment:
      POSTGRES_DB: todo
      POSTGRES_USER: postgres_user
      POSTGRES_PASSWORD: postgres_pass
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      SECRET_KEY: your-secret-key-here
      DEBUG: "True"
      ALLOWED_HOSTS: localhost,127.0.0.1
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

> **Atenção:** o backend precisa de `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` mesmo aqui — o `core/settings.py` exige essas variáveis via `pydantic-settings` independente de rede/banco. Se faltar alguma, o container do backend sobe e morre imediatamente (visível com `docker compose ps` mostrando status `Exited` e detalhado em `docker compose logs backend`).

> **Atenção:** o `frontend` depende do `backend` mesmo sem trocar dados de configuração — o Nginx faz a resolução DNS do host em `proxy_pass` **uma única vez, na inicialização**. Sem esse `depends_on`, o Compose sobe os dois containers em paralelo e, como o `backend` só fica pronto depois que o `db` passa no healthcheck (alguns segundos), o Nginx quase sempre inicia primeiro, não encontra o host `backend` ainda registrado no DNS interno do Compose, e **recusa subir** (`nginx: [emerg] host not found in upstream "backend"`) — reproduzível em praticamente todo `docker compose up -d` a partir do zero.

---

## Parte 2 — Subindo a Stack

Remova qualquer container manual das aulas anteriores para evitar conflito de nomes e portas:

```bash
docker rm -f backend db teste-db todo-backend todo-frontend 2>/dev/null
```

Suba a stack completa:

```bash
docker compose up -d
```

Acompanhe os logs de todos os serviços:

```bash
docker compose logs -f
```

Você deve ver o backend esperando o banco ficar saudável antes de rodar as migrations.

---

## Parte 3 — Confirmando o Funcionamento

Liste os containers da stack:

```bash
docker compose ps
```

Todos os serviços devem aparecer com status `running` (ou `healthy` no caso do banco).

Teste o backend, acessando no navegador: `http://localhost:8000/api/tasks/`

Teste o frontend no navegador:

```
http://localhost:4200
```

Confirme que o frontend consegue listar as tarefas vindas do backend.

---

## Parte 4 — Acessando um Container em Execução

Entre no container do backend para explorar o ambiente:

```bash
docker compose exec backend sh
```

Dentro do container, confirme que as variáveis de ambiente estão configuradas:

```bash
env | grep POSTGRES_
```

Saia do container:

```bash
exit
```

---

## Parte 5 — Encerrando a Stack

Quando terminar os testes:

```bash
docker compose down
```

Se quiser remover também o volume do banco (cuidado, isso apaga os dados):

```bash
docker compose down -v
```

---

## Checklist final do dia

- [ ] `docker-compose.yml` criado na raiz do projeto
- [ ] `healthcheck` configurado no banco
- [ ] `depends_on` com `condition: service_healthy` no backend
- [ ] Banco sem `ports:` no arquivo
- [ ] `docker compose up -d` sobe todos os serviços sem erro
- [ ] Frontend consegue listar tarefas vindas do backend

---

## Material de apoio

- Docker Compose — referência do arquivo: https://docs.docker.com/reference/compose-file/
- Docker Compose — healthcheck: https://docs.docker.com/reference/compose-file/services/#healthcheck
- Docker Compose — comandos CLI: https://docs.docker.com/reference/cli/docker/compose/
