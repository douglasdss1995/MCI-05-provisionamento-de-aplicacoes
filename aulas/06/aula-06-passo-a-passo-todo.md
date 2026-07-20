# Aula 06 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-06-passo-a-passo-catalogo.md`.

## Antes de começar

Confirme que a stack da Aula 05 sobe corretamente com o `.env`:

```bash
docker compose up -d
```

---

## Parte 1 — Criando o nginx.conf da Stack

Na raiz do projeto, crie uma pasta `nginx/` e dentro dela o arquivo `nginx.conf`:

```
# nginx/nginx.conf
# Gateway unico da aplicacao: roteia para o frontend e para a API do backend

upstream backend_upstream {
    server backend:8000;
}

server {
    listen 80;

    # Arquivos estaticos do Django (admin, bibliotecas)
    location /static/ {
        alias /app/staticfiles/;
    }

    # Todas as chamadas de API vao para o backend Django
    location /api/ {
        proxy_pass http://backend_upstream/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # O Django Admin tambem precisa ser encaminhado ao backend —
    # sem este bloco, /admin/ cairia no catch-all do Angular abaixo
    # e devolveria o index.html no lugar da tela de login do Admin
    location /admin/ {
        proxy_pass http://backend_upstream/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Tudo o mais vai para o frontend Angular — o frontend roda em seu
    # proprio container Nginx (que ja resolve o roteamento da SPA), entao
    # aqui so encaminhamos a requisicao para ele, sem tentar servir arquivo
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> **Atenção:** `location /` faz `proxy_pass` para o serviço `frontend`, **não** serve arquivos diretamente (`root`/`try_files`) como nas aulas anteriores. Esse container Nginx (o "gateway") nunca recebe os arquivos compilados do Angular — quem tem esses arquivos é o container `frontend`, criado a partir da imagem do `frontend/Dockerfile`. Se você tentar servir os arquivos aqui com `root /usr/share/nginx/html`, vai ver a página padrão "Welcome to nginx!" no lugar da aplicação, porque essa pasta está vazia dentro *deste* container.

---

## Parte 2 — Ajustando o Dockerfile do Frontend

O frontend não precisa mais resolver `/api/` nem `/admin/` — isso agora é responsabilidade do Nginx da stack (Parte 1). Mas ele **continua precisando** do próprio `try_files` para lidar com rotas internas do Angular (ex: dar F5 em `/tarefas/1`) — sem isso, a config padrão do `nginx:alpine` devolve 404 para qualquer rota que não seja a raiz.

**O que é o `nginx-spa.conf`:** é a configuração do Nginx que roda dentro do container do frontend (o estágio final do Dockerfile multi-stage, baseado em `nginx:alpine`). A partir de agora ele tem uma única responsabilidade — servir os arquivos estáticos gerados pelo `ng build` e resolver o roteamento client-side do Angular (SPA). Ele deixa de conhecer `/api/` e `/admin/`: quem cuida disso é o Nginx da stack (`nginx/nginx.conf`, Parte 1), que fica na frente de todos os containers como gateway único e só repassa (`proxy_pass`) para o `frontend` o que não é `/api/`, `/admin/` ou `/static/`.

O `try_files` continua sendo a linha mais importante do arquivo: o Angular Router controla rotas como `/tarefas/3` só no navegador — esse caminho não existe como arquivo dentro do container. Sem o `try_files`, uma requisição direta a `/tarefas/3` (ou um F5 nessa rota) faria o Nginx procurar um arquivo chamado `tarefas/3` no disco, não encontrar e devolver 404. Com ele, o Nginx cai no `index.html` e deixa o próprio Angular decidir o que renderizar.

Crie o arquivo `frontend/nginx-spa.conf`, com uma configuração enxuta, só de SPA:

```nginx
# nginx-spa.conf
#
# Configuração do Nginx dentro do container do frontend (estágio final do
# Dockerfile multi-stage, a partir da imagem "nginx:alpine").
#
# Responsabilidade única deste arquivo: servir os arquivos estáticos
# gerados pelo `ng build` (HTML, JS, CSS) e resolver o roteamento
# client-side do Angular (SPA — Single Page Application). Ele não conhece
# a API nem o admin do Django — quem cuida disso é o Nginx da stack
# (nginx/nginx.conf), que fica na frente de todos os containers como
# gateway único e repassa (proxy_pass) para este container apenas o que
# não for /api/, /admin/ ou /static/.
#
# Por que o try_files importa: o Angular Router controla as rotas no
# navegador (ex.: /tarefas/3), mas esse caminho não existe como arquivo
# real dentro do container. Sem o try_files abaixo, uma requisição direta
# a /tarefas/3 (ou um F5 nessa rota) faria o Nginx procurar um arquivo
# chamado "tarefas/3" no disco, não encontrar e devolver 404 — mesmo a
# rota sendo válida para o Angular. O try_files intercepta esse caso e
# devolve o index.html, deixando o próprio Angular decidir o que renderizar.

server {
    # Porta em que este Nginx escuta dentro do container. Não é exposta ao
    # host diretamente — quem recebe as requisições externas é o gateway
    # (nginx/nginx.conf), que enxerga este container pelo nome do serviço
    # (ex.: "frontend") na rede interna do Compose.
    listen 80;

    # Aceita qualquer Host recebido — o gateway já resolveu isso antes de
    # repassar a requisição, então não há necessidade de validar domínio aqui.
    server_name _;

    # Pasta onde o Dockerfile copiou a saída do `ng build` (dist/.../browser).
    # É a raiz de onde este Nginx busca arquivos para qualquer location abaixo.
    root /usr/share/nginx/html;

    # Arquivo servido por padrão quando a rota pedida aponta para um diretório.
    index index.html;

    location / {
        # Ordem de tentativa: 1) arquivo com esse nome exato; 2) diretório
        # com esse nome; 3) se nenhum existir, cai no index.html — é esse
        # passo 3 que resolve o F5 em rotas internas do Angular (fallback de SPA).
        try_files $uri $uri/ /index.html;
    }

    # Arquivos estáticos com hash no nome (o build do Angular gera nomes
    # como main.a1b2c3.js) podem ter cache agressivo no navegador: como o
    # hash muda sempre que o conteúdo muda, não há risco de servir uma
    # versão antiga em cache.
    location ~* \.(js|css|png|jpg|svg|ico|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Simplifique o `frontend/Dockerfile` para usar essa configuração enxuta:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine AS runner

# Remove a configuracao padrao do Nginx (nao tem fallback de SPA)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist/todo-frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## Parte 3 — Configurando o collectstatic no Backend

No `backend/Dockerfile`, adicione o comando de `collectstatic` antes de iniciar o Gunicorn. Atualize o `CMD` para um script de entrypoint:

Crie o arquivo `backend/entrypoint.sh`:

```bash
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
```

Dê permissão de execução:

```bash
chmod +x backend/entrypoint.sh
```

Atualize o arquivo `backend/Dockerfile`:

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

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
```

---

## Parte 4 — Atualizando o docker-compose.yml

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
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles

  frontend:
    build: ./frontend

  nginx:
    image: nginx:alpine
    depends_on:
      - backend
      - frontend
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles

volumes:
  todo-db-data:
  static_volume:
```

Note que `backend` e `frontend` não têm mais `ports:` — apenas o `nginx` expõe a porta 80.

---

## Parte 5 — Subindo a Stack Completa

```bash
docker compose down
docker compose up -d --build
```

Acompanhe os logs do backend para confirmar que o `collectstatic` e o `migrate` rodaram:

```bash
docker compose logs backend
```

---

## Parte 6 — Testando

Acesse a aplicação pelo Nginx, na porta 80:

```
http://localhost/
```

Teste a API através do proxy, acessando no navegador: `http://localhost/api/tasks/`

Acesse o Django Admin e confirme que o CSS carrega corretamente:

```
http://localhost/admin/
```

Se a tela do admin aparecer estilizada, o `collectstatic` e o volume compartilhado estão funcionando.

Por fim, repita o teste de roteamento da Aula 02 — agora através do gateway:

1. Navegue para qualquer rota interna da aplicação (ex: uma tela de detalhes de tarefa)
2. Pressione F5 para recarregar a página
3. Se a página carregar normalmente (sem erro 404), o `nginx-spa.conf` do frontend está funcionando corretamente por trás do gateway

---

## Checklist final do dia

- [ ] `nginx.conf` criado com proxy para a API, o admin **e** o frontend (`location /` com `proxy_pass`, não `root`/`try_files`)
- [ ] `frontend/nginx-spa.conf` criado e usado no `Dockerfile` do frontend (sem ele, F5 numa rota interna do Angular quebra com 404)
- [ ] `entrypoint.sh` criado e executável
- [ ] `docker-compose.yml` atualizado com o serviço `nginx`
- [ ] Backend e frontend sem portas expostas para o host
- [ ] Frontend acessível em `localhost`
- [ ] API acessível em `localhost/api/`
- [ ] Navegação entre rotas testada sem erro 404 no F5 (mesmo teste da Aula 02, agora através do gateway)
- [ ] Django Admin com CSS funcionando

---

## Material de apoio

- Nginx — proxy_pass: https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- Django — collectstatic: https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/
- Let's Encrypt — como funciona: https://letsencrypt.org/how-it-works/
- Certbot — documentação oficial: https://certbot.eff.org/
