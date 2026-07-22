# Aula 07 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-07-passo-a-passo-catalogo.md`.

## Antes de começar

Até aqui você trabalhou dentro do clone do repositório do curso, na subpasta `apps/todo`. A partir de hoje a Lista de Tarefas passa a viver em um repositório **próprio e independente**, no seu GitHub: é lá que o GitHub Actions vai rodar e publicar imagens. A primeira parte desta aula cuida dessa migração; depois disso seguimos com o pipeline de CI.

---

## Parte 1 — Criando um Repositório Próprio para a Lista de Tarefas

### Por que a aplicação precisa de um repositório só dela

O workflow de CI que vamos criar espera duas coisas que só funcionam se `backend/` e `frontend/` estiverem na **raiz** do repositório: o `working-directory: backend` de cada step, e o próprio GitHub Actions, que só descobre workflows em `.github/workflows/` quando esse caminho está na raiz — um `.github/workflows/` dentro de uma subpasta como `apps/todo/` nunca é executado. Como no repositório do curso `apps/todo` é só uma subpasta entre várias (`apps/catalogo`, `apps/chamados`, `aulas/`...), a Lista de Tarefas precisa migrar para um repositório GitHub dela mesma, com `backend/` e `frontend/` na raiz.

O workflow também precisa publicar pacotes no `ghcr.io` e usar segredos do repositório (`secrets.GITHUB_TOKEN`) — coisas que só funcionam em um repositório onde você tem permissão de escrita, o que também aponta para um repositório seu, e não o clone do professor.

### Criando o repositório no GitHub

No navegador, crie um repositório novo e vazio (sem README, sem `.gitignore`, sem licença) chamado `todo-app`:

```
https://github.com/new
```

Ao final, você terá um repositório vazio em:

```
https://github.com/SEU-USUARIO/todo-app
```

### Copiando o projeto para uma pasta própria

De volta ao terminal (WSL), copie o conteúdo de `apps/todo` (do clone do curso feito na Aula 01) para uma pasta nova, fora do repositório do curso:

```bash
mkdir -p ~/todo-app
cp -r ~/MCI-05-provisionamento-de-aplicacoes/apps/todo/. ~/todo-app/
cd ~/todo-app
```

Essa cópia não traz histórico de commits — é só o estado atual dos arquivos, o que é suficiente aqui. A partir de agora, todo o trabalho da Lista de Tarefas acontece em `~/todo-app`, não mais dentro do clone do curso.

### Inicializando o Git e enviando para o GitHub

```bash
git init
git add .
git commit -m "Estrutura inicial: Lista de Tarefas"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/todo-app.git
git push -u origin main
```

Substitua `SEU-USUARIO` pelo seu nome de usuário no GitHub. Confirme no navegador que `backend/` e `frontend/` aparecem na raiz do repositório `todo-app`.

A partir de agora, `git push origin main` dentro de `~/todo-app` envia para o **seu** repositório — é nele que o workflow de CI desta aula vai rodar.

---

## Parte 2 — Criando a Estrutura do Workflow

Na raiz do projeto, crie as pastas necessárias:

```bash
mkdir -p .github/workflows
```

---

## Parte 3 — Escrevendo o Workflow de CI

Crie o arquivo `.github/workflows/ci.yml`:

```yaml
# .github/workflows/ci.yml
# Pipeline de integracao continua: lint, testes e build da imagem Docker

name: CI

# Gatilhos do pipeline — aqui estao varios exemplos de "on" possiveis,
# a maioria comentada. Deixamos ativos push (qualquer branch) e
# pull_request, que sao os dois gatilhos que este curso usa de fato.
on:
  # Roda a cada push, em QUALQUER branch (nao so na main) —
  # util para pegar erro cedo, antes mesmo de abrir o pull request
  push:
    branches: ["**"]

  # Roda quando um pull request e aberto, recebe novos commits,
  # ou e reaberto, tendo como alvo qualquer branch do repositorio —
  # é o que garante que o codigo é validado antes do merge
  pull_request:
    branches: ["**"]
    types: [opened, synchronize, reopened]

  # Exemplo: permite disparar o pipeline manualmente pela aba
  # Actions do GitHub, sem precisar de push ou pull request
  # workflow_dispatch:

  # Exemplo: roda o pipeline em um horario agendado (cron),
  # como uma checagem periodica independente de mudanca no codigo
  # schedule:
  #   - cron: "0 6 * * 1"  # toda segunda-feira as 06:00 UTC

  # Exemplo: roda quando uma release e publicada no repositorio,
  # util para pipelines que fazem deploy apenas em versoes marcadas
  # release:
  #   types: [published]

  # Exemplo: roda quando uma tag no padrao vX.Y.Z e enviada,
  # outra forma comum de disparar builds de versao
  # push:
  #   tags: ["v*.*.*"]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    env:
      POSTGRES_DB: todo
      POSTGRES_USER: postgres_user
      POSTGRES_PASSWORD: postgres_pass
      POSTGRES_HOST: localhost
      POSTGRES_PORT: 5432
      SECRET_KEY: chave-secreta-apenas-para-ci-nao-usar-em-producao
      DEBUG: "True"
      ALLOWED_HOSTS: "localhost,127.0.0.1"

    # Sobe um PostgreSQL temporario para os testes de integracao —
    # sem isso, o pytest-django nao consegue criar o banco de teste
    # e o job falha mesmo com o codigo correto
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: todo
          POSTGRES_USER: postgres_user
          POSTGRES_PASSWORD: postgres_pass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      # Copia o codigo do repositorio para dentro do runner do GitHub Actions —
      # sem esse step nao existe codigo nenhum disponivel nos proximos steps
      - name: Faz checkout do codigo
        uses: actions/checkout@v4

      # Instala o uv (gerenciador de dependencias Python usado no curso)
      # dentro do runner, disponibilizando o comando `uv` para os steps seguintes
      - name: Instala o uv
        uses: astral-sh/setup-uv@v3

      # Le o pyproject.toml/uv.lock do backend e instala as dependencias
      # (Django, DRF, pytest, ruff etc.) em um ambiente isolado do runner
      - name: Instala as dependencias do backend
        run: uv sync
        working-directory: backend

      # Roda o linter ruff sobre todo o backend; falha o job se encontrar
      # codigo fora do padrao (imports nao usados, linha longa, etc.)
      - name: Verifica o estilo do codigo com ruff
        run: uv run ruff check .
        working-directory: backend

      # `manage.py check` valida a configuracao do Django (models, settings,
      # apps instalados) sem precisar de banco de dados — pega erro de
      # configuracao antes mesmo de chegar nos testes
      - name: Verifica a configuracao do Django
        run: uv run python manage.py check
        working-directory: backend

      # Roda em modo --dry-run: nao cria nenhuma migration de fato, só avisa
      # se falta gerar uma. Falha o pipeline quando um model foi alterado e
      # o desenvolvedor esqueceu de rodar `makemigrations` localmente
      - name: Verifica se as migrations estao sincronizadas com os models
        run: uv run python manage.py makemigrations --check --dry-run
        working-directory: backend

      # Aplica as migrations de verdade contra o Postgres do serviço acima,
      # confirmando que elas rodam sem erro num banco limpo — diferente do
      # banco de teste que o pytest-django cria e destroi por conta propria
      - name: Aplica as migrations no banco de dados
        run: uv run python manage.py migrate
        working-directory: backend

      # Executa a suite de testes automatizados (pytest + pytest-django)
      # contra o banco ja migrado; é o ultimo — e mais demorado — checkpoint
      # antes de considerar o codigo pronto para virar imagem
      - name: Executa os testes automatizados
        run: uv run pytest
        working-directory: backend

  build-and-push:
    needs: lint-and-test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      # Job novo roda em uma maquina (runner) limpa e separada da anterior,
      # entao o codigo precisa ser baixado de novo aqui
      - name: Faz checkout do codigo
        uses: actions/checkout@v4

      # Autentica no GitHub Container Registry usando o proprio ator do
      # workflow (github.actor) e um token temporario gerado automaticamente
      # pelo GitHub (secrets.GITHUB_TOKEN) — nao é preciso criar segredo manual
      - name: Autentica no GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Builda a imagem Docker do backend a partir do Dockerfile em ./backend
      # e, com push: true, envia (`docker push`) o resultado direto para o
      # ghcr.io com a tag `backend:latest`
      - name: Constroi e publica a imagem do backend
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:latest
```

Cada step do job `lint-and-test` está comentado no arquivo acima, na ordem em que executa: checkout do código, instalação do `uv`, instalação das dependências, lint com `ruff`, checagem de configuração do Django, checagem de migrations pendentes, aplicação das migrations e, por fim, os testes automatizados. O job `build-and-push` só começa depois que `lint-and-test` termina com sucesso (`needs: lint-and-test`) e faz três coisas: baixa o código de novo (runner isolado), autentica no `ghcr.io` e constrói/publica a imagem do backend.

Repare também no bloco `on:` no topo do arquivo: `push` em `branches: ["**"]` roda o pipeline em qualquer branch, não só na `main` — assim você recebe feedback do lint e dos testes antes mesmo de abrir o pull request. O `pull_request` roda quando o PR é aberto, recebe novos commits (`synchronize`) ou é reaberto, e é o gatilho que de fato bloqueia um merge com código quebrado. Os demais gatilhos (`workflow_dispatch`, `schedule`, `release`, `push` por tag) estão comentados de propósito: não fazem parte do pipeline deste curso, mas servem de referência para quando você precisar disparar um pipeline manualmente, numa agenda fixa, ao publicar uma release, ou por uma tag de versão.

Um detalhe importante: como o job `build-and-push` depende de `lint-and-test` e não tem nenhuma restrição de branch, ele publica a imagem no `ghcr.io` a cada push em qualquer branch e a cada pull request — inclusive antes do merge. Isso é aceitável aqui, só para fins didáticos (queremos ver o pipeline completo rodando com frequência), mas numa aplicação real você normalmente restringiria esse job com algo como `if: github.ref == 'refs/heads/main'`, para só publicar imagens a partir da `main`.

---

## Parte 4 — Ajustando Permissões do Repositório

Nas configurações do seu repositório no GitHub, acesse:

```
Settings → Actions → General → Workflow permissions
```

Marque a opção **Read and write permissions** para que o workflow consiga publicar imagens no `ghcr.io`.

---

## Parte 5 — Testando o Pipeline com um Erro Proposital

Introduza um erro de lint no código do backend (por exemplo, uma linha muito longa ou uma variável não usada). Envie para o GitHub:

```bash
git add .
git commit -m "teste: erro proposital de lint"
git push origin main
```

Acesse a aba **Actions** do seu repositório no GitHub e observe o job `lint-and-test` falhar.

---

## Parte 6 — Corrigindo e Confirmando o Pipeline Verde

Corrija o erro introduzido:

```bash
uv run ruff check . --fix
```

Envie a correção:

```bash
git add .
git commit -m "fix: corrige erro de lint"
git push origin main
```

Acompanhe novamente a aba **Actions** e confirme que os dois jobs (lint-and-test e build-and-push) terminam com sucesso.

---

## Parte 7 — Confirmando a Imagem Publicada

No GitHub, acesse:

```
https://github.com/SEU-USUARIO/todo-app/pkgs/container/backend
```

Você deve ver a imagem publicada com a tag `latest`.

---

## Checklist final do dia

- [ ] Repositório `todo-app` criado no seu GitHub
- [ ] Projeto copiado para `~/todo-app`, com `backend/` e `frontend/` na raiz
- [ ] Repositório local inicializado e enviado (`push`) para `todo-app`
- [ ] `.github/workflows/ci.yml` criado
- [ ] Permissões de workflow ajustadas no repositório
- [ ] Pipeline executando `ruff check`, `manage.py check`, checagem de migrations e `pytest`
- [ ] Pipeline falhando com erro proposital (teste de sanidade)
- [ ] Pipeline verde após a correção
- [ ] Imagem publicada visível no `ghcr.io`

---

## Material de apoio

- GitHub — Criando um novo repositório: https://docs.github.com/pt/repositories/creating-and-managing-repositories/quickstart-for-repositories
- GitHub Actions — documentação oficial: https://docs.github.com/actions
- GitHub Container Registry: https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- docker/build-push-action: https://github.com/docker/build-push-action
- astral-sh/setup-uv: https://github.com/astral-sh/setup-uv
- Django — `manage.py check`: https://docs.djangoproject.com/en/5.0/ref/django-admin/#check
- Django — `makemigrations`: https://docs.djangoproject.com/en/5.0/ref/django-admin/#makemigrations
