# Aula 02 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-02-passo-a-passo-catalogo.md`.

## Antes de começar

Confirme que você concluiu o checklist da Aula 01. Você vai precisar do repositório clonado e do Docker Engine funcionando.

Entre na pasta do projeto:

```bash
cd MCI-05-provisionamento-de-aplicacoes
```

---

## Parte 1 — Dockerfile do Backend Django

Entre na pasta do `apps/todo/backend`:

```bash
cd apps/todo/backend
```

Confirme que o container `meu-postgres`, criado na Aula 01, ainda está rodando:

```bash
docker ps --filter name=meu-postgres
```

Se ele não aparecer na lista, suba-o novamente com o mesmo comando da Aula 01:

```bash
docker run -d --name meu-postgres -e POSTGRES_PASSWORD=etech123 -p 5432:5432 postgres:16
```

Copie o arquivo `.env.example` para `.env`.

Crie um arquivo chamado `.dockerignore` na mesma pasta, com o seguinte conteúdo:

```
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
staticfiles/
.git/
```

Isso evita copiar a virtualenv e arquivos de cache para dentro da imagem. Em especial, o `.env` **não deve** ser copiado para a imagem — ele contém segredos e será passado ao container em tempo de execução, com `--env-file`, e não em tempo de build.

Crie um arquivo chamado `Dockerfile` (sem extensão) com o seguinte conteúdo:

```dockerfile
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

EXPOSE 8000

# Comando executado quando o container inicia
CMD ["uv", "run", "gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Construa a imagem:

```bash
docker build -t todo-backend:v1 .
```

### Conectando o backend ao banco de dados

O Django, dentro do container, precisa alcançar o Postgres (`meu-postgres`) pela rede do Docker. Containers na rede `bridge` padrão não se resolvem por nome — é preciso colocar os dois em uma rede criada por você:

```bash
docker network create todo-network
docker network connect todo-network meu-postgres
```

> Se o `meu-postgres` já estiver conectado a essa rede (por exemplo, se você repetir o exercício), o segundo comando vai falhar com "endpoint already exists" — pode ignorar.

O `meu-postgres`, criado na Aula 01, só tem o usuário/banco padrão `postgres`. O `.env.example` do backend usa credenciais próprias da aplicação (usuário `postgres_user`, banco `todo`), então é preciso criar esse usuário e esse banco dentro do `meu-postgres` antes de continuar:

```bash
docker exec meu-postgres psql -U postgres -c "CREATE USER postgres_user WITH PASSWORD 'postgres_pass';"
docker exec meu-postgres psql -U postgres -c "CREATE DATABASE todo OWNER postgres_user;"
```

> `postgres_user`/`postgres_pass` é o usuário e senha padrão usados pelas três aplicações do curso (Lista de Tarefas, Catálogo e Chamados). Isso não é uma boa prática de produção — o ideal é cada aplicação ter suas próprias credenciais — mas simplifica o curso e evita confusão entre os projetos. Só o nome do banco (`POSTGRES_DB`) muda de uma aplicação para outra.

Edite o `.env` e ajuste `POSTGRES_HOST` e `POSTGRES_PORT` para apontar para o `meu-postgres` pela rede do Docker:

```
POSTGRES_HOST=meu-postgres
POSTGRES_PORT=5432
```

A porta `5432` aqui é a **porta interna** do container do Postgres — a mesma sempre, independente de qual porta você publicou no host com `-p` (5432, 5433 ou qualquer outra). Comunicação entre containers usa a porta em que o processo escuta *dentro* do container, não a porta publicada no host.

Execute o container do backend conectado a essa rede e passando o arquivo de variáveis de ambiente:

```bash
docker run -d --name todo-backend --network todo-network --env-file .env -p 8000:8000 todo-backend:v1
```

Aplique as migrations dentro do container (cria as tabelas no banco de dados):

```bash
docker exec todo-backend uv run manage.py migrate
```

Acesse: `http://localhost:8000/api/tasks/`

Se retornar uma resposta JSON (mesmo que vazia), o backend está funcionando e realmente conversando com o Postgres.

**Deixe esse container rodando** — na Parte 2 o frontend vai precisar conversar com ele. Só pare e remova os dois ao final da aula (veja a seção de limpeza).

---

## Parte 2 — Dockerfile Multi-stage do Frontend Angular

Volte para a raiz do projeto e entre na pasta do frontend:

```bash
cd ../frontend
```

Confirme o nome do seu projeto Angular no arquivo `angular.json` — o caminho de saída do build depende desse nome. Procure pelo campo `outputPath`.

O frontend chama a API sempre com caminho relativo (`/api/tasks/`, veja `task.service.ts`) — quem precisa encaminhar essas chamadas para o backend é o próprio Nginx do frontend, com um `proxy_pass`. Sem isso, o Nginx trataria `/api/tasks/` como uma rota do Angular e devolveria o `index.html` no lugar do JSON.

Crie o arquivo `nginx.conf` na raiz da pasta `frontend/`:

```nginx
server {
    # Porta em que o Nginx escuta dentro do container (mapeada para 4200 no host)
    listen 80;

    # Pasta onde ficam os arquivos compilados do Angular (copiados no Dockerfile)
    root /usr/share/nginx/html;

    # Arquivo servido por padrão quando a rota pedida é um diretório
    index index.html;

    # Qualquer requisição que comece com /api/ é uma chamada à API Django,
    # não uma rota do Angular — encaminha para o container do backend.
    location /api/ {
        # todo-backend é o nome do container (resolvido por DNS porque os dois
        # estão na mesma rede "todo-network") e 8000 é a porta interna do Gunicorn.
        # Sem barra no final da URL, o Nginx repassa a URI original (ex: /api/tasks/) sem alterar.
        proxy_pass http://todo-backend:8000;

        # Preserva o Host original da requisição (o navegador pediu "localhost:4200")
        proxy_set_header Host $host;

        # Os cabeçalhos abaixo informam ao backend o IP e o protocolo reais do
        # cliente, já que a requisição chega até ele através do proxy
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Qualquer outra rota é tratada pelo Angular (SPA)
    location / {
        # Tenta servir o arquivo pedido; se não existir, devolve o index.html
        # e deixa o Angular decidir o que renderizar — é isso que permite
        # dar F5 em uma rota interna (ex: /tarefas/1) sem cair em 404 no Nginx.
        try_files $uri $uri/ /index.html;
    }
}
```

`todo-backend` só é resolvido por nome porque os dois containers vão estar na mesma rede (`todo-network`), criada na Parte 1 — e a porta `8000` é a porta interna do container do backend (a mesma definida no `EXPOSE 8000` do Dockerfile dele).

Crie o arquivo `Dockerfile` na raiz da pasta `frontend/`:

```dockerfile
# Dockerfile multi-stage do frontend Angular - Lista de Tarefas

# Estagio 1: compila a aplicacao Angular
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Estagio 2: imagem final, apenas com Nginx servindo os arquivos compilados
FROM nginx:alpine AS runner

# Ajuste o caminho abaixo conforme o outputPath do seu angular.json
# (o projeto do curso usa "todo-frontend" como nome do projeto Angular)
COPY --from=builder /app/dist/todo-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Construa a imagem:

```bash
docker build -t todo-frontend:v1 .
```

Execute o container conectado à mesma rede do backend, para que o `proxy_pass` consiga alcançar `todo-backend`:

```bash
docker run -d --name todo-frontend --network todo-network -p 4200:80 todo-frontend:v1
```

Acesse no navegador:

```
http://localhost:4200
```

### Testando a comunicação com o backend

1. A lista de tarefas deve carregar na tela (mesmo que vazia) — isso confirma que o `proxy_pass` está encaminhando `/api/tasks/` corretamente para o `todo-backend`
2. Se aparecer a mensagem de erro "Verifique se o servidor está rodando", confira se os dois containers estão na mesma rede (`docker network inspect todo-network`) e se o `todo-backend` está de pé

### Testando o roteamento

1. Navegue para qualquer rota interna da aplicação (por exemplo, uma tela de detalhes de tarefa)
2. Pressione F5 para recarregar a página
3. Se a página carregar normalmente (sem erro 404), o `try_files` está funcionando

---

## Limpeza

Ao terminar os testes da Parte 1 e da Parte 2, pare e remova os containers:

```bash
docker stop todo-backend todo-frontend
docker rm todo-backend todo-frontend
```

O `meu-postgres` pode continuar rodando — ele é reaproveitado nas próximas aulas.

---

## Checklist final do dia

- [ ] `.dockerignore` do backend criado (sem `.env`, `.venv`, cache)
- [ ] Dockerfile do backend criado e imagem construída sem erros
- [ ] Rede Docker (`todo-network`) criada e `meu-postgres` conectado a ela
- [ ] Migrations aplicadas dentro do container do backend
- [ ] Container do backend responde em `localhost:8000` com dados reais do banco
- [ ] Dockerfile multi-stage do frontend criado e imagem construída sem erros
- [ ] `nginx.conf` criado com `try_files` **e** `proxy_pass` de `/api/` para `todo-backend`
- [ ] Container do frontend rodando na mesma rede do backend (`todo-network`)
- [ ] Lista de tarefas carrega em `localhost:4200` (frontend conversando com o backend)
- [ ] Navegação entre rotas testada sem erro 404 no F5

---

## Material de apoio

- Dockerfile — referência oficial: https://docs.docker.com/reference/dockerfile/
- Multi-stage builds — documentação oficial: https://docs.docker.com/build/building/multi-stage/
- uv — imagem Docker oficial: https://docs.astral.sh/uv/guides/integration/docker/
- Nginx — try_files: https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files