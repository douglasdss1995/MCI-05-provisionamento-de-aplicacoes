# Aula 03 — Exercício do Aluno (Catálogo de Filmes)

> **Sua vez — Catálogo de Filmes.** Agora que acompanhamos a demonstração do professor com a Lista de Tarefas (`aula-03-passo-a-passo-todo.md`), repita sozinho o mesmo padrão na segunda aplicação do curso.

## Antes de começar

Certifique-se de que as imagens `catalogo-backend:v1` e `catalogo-frontend:v1` da Aula 02 ainda existem:

```bash
docker images
```

---

## Parte 1 — Comprovando a Efemeridade

Suba um container PostgreSQL sem volume:

```bash
docker run -d --name teste-db-catalogo -e POSTGRES_PASSWORD=teste123 -p 5435:5432 postgres:16
```

Aguarde alguns segundos e conecte via DBeaver (host `localhost`, porta `5435`, usuário `postgres`, senha `teste123`). Crie uma tabela simples e insira um registro:

```sql
CREATE TABLE prova (id SERIAL PRIMARY KEY, nome TEXT);
INSERT INTO prova (nome) VALUES ('este dado vai sumir');
```

Agora remova o container:

```bash
docker stop teste-db-catalogo
docker rm teste-db-catalogo
```

Suba um novo container com o mesmo nome:

```bash
docker run -d --name teste-db-catalogo -e POSTGRES_PASSWORD=teste123 -p 5435:5432 postgres:16
```

Conecte de novo pelo DBeaver e tente consultar a tabela `prova`. Ela não existe mais — os dados se perderam junto com o container anterior.

Remova este container de teste:

```bash
docker stop teste-db-catalogo
docker rm teste-db-catalogo
```

---

## Parte 2 — Criando um Volume Persistente

Crie um volume nomeado:

```bash
docker volume create catalogo-db-data
```

Suba o PostgreSQL usando esse volume:

```bash
docker run -d --name catalogo-db \
  -e POSTGRES_DB=catalogo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v catalogo-db-data:/var/lib/postgresql/data \
  -p 5435:5432 \
  postgres:16
```

> Publicamos na porta `5435` do host (em vez de `5432`) para não colidir com o `todo-db` da Lista de Tarefas, caso ele ainda esteja de pé. A porta interna do container continua sendo `5432`.

Conecte pelo DBeaver e crie uma tabela de teste, igual ao passo anterior.

Remova o container (sem remover o volume):

```bash
docker stop catalogo-db
docker rm catalogo-db
```

Suba o container de novo, usando o mesmo volume:

```bash
docker run -d --name catalogo-db \
  -e POSTGRES_DB=catalogo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v catalogo-db-data:/var/lib/postgresql/data \
  -p 5435:5432 \
  postgres:16
```

Consulte a tabela de teste novamente. Desta vez os dados devem estar lá.

---

## Parte 3 — Criando uma Rede e Conectando o Backend

Crie a rede do projeto (se ainda não tiver criado na Aula 02):

```bash
docker network create catalogo-network
```

Remova o container `catalogo-db` atual (o volume continua guardando os dados):

```bash
docker stop catalogo-db
docker rm catalogo-db
```

Suba o PostgreSQL novamente, agora dentro da rede:

```bash
docker run -d --name catalogo-db \
  --network catalogo-network \
  -e POSTGRES_DB=catalogo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v catalogo-db-data:/var/lib/postgresql/data \
  postgres:16
```

Observe que este container não tem `-p` — não precisamos acessá-lo diretamente do host, apenas o backend vai falar com ele.

Suba o backend na mesma rede, com as variáveis de ambiente apontando para o banco:

```bash
docker run -d --name catalogo-backend \
  --network catalogo-network \
  -e POSTGRES_DB=catalogo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -e POSTGRES_HOST=catalogo-db \
  -e POSTGRES_PORT=5432 \
  -e SECRET_KEY=your-secret-key-here \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -p 8001:8000 \
  catalogo-backend:v1
```

Repare que `POSTGRES_HOST=catalogo-db` usa o **nome do container**, não um IP. Publicamos em `8001` no host (em vez de `8000`) para não colidir com o `todo-backend` da Lista de Tarefas.

> **Atenção:** diferente da Aula 02 (que usava `--env-file .env`, carregando todas as variáveis de uma vez), aqui estamos passando cada variável individualmente com `-e`. Isso significa que **toda** variável que o Django exige precisa aparecer na lista — inclusive `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS`, que não têm relação com rede/banco mas são obrigatórias no `core/settings.py` (via `pydantic-settings`). Se esquecer alguma, o container sobe e morre imediatamente (`docker ps -a` mostra `Exited`), e `docker exec` reclama que o container não está rodando. Para investigar esse tipo de falha, use `docker logs catalogo-backend`.

---

## Parte 4 — Rodando as Migrations

Execute as migrations do Django dentro do container em execução:

```bash
docker exec -it catalogo-backend uv run python manage.py migrate
```

Acesse: `http://localhost:8001/api/movies/`

---

## Parte 5 — Inspecionando os Containers

Veja os detalhes de rede e variáveis de ambiente do backend:

```bash
docker inspect catalogo-backend
```

Procure pelas seções `NetworkSettings` e `Env` no resultado.

---

## Checklist final do dia

- [ ] Efemeridade comprovada (dados perdidos sem volume)
- [ ] Volume nomeado (`catalogo-db-data`) criado e persistência comprovada
- [ ] Rede `catalogo-network` criada
- [ ] Container do banco rodando sem porta exposta para o host
- [ ] Backend conectado ao banco pelo nome do container
- [ ] Migrations executadas com sucesso

---

## Material de apoio

- Docker Volumes — documentação oficial: https://docs.docker.com/engine/storage/volumes/
- Docker Networks — documentação oficial: https://docs.docker.com/engine/network/
- docker inspect — referência: https://docs.docker.com/reference/cli/docker/inspect/
