# Aula 03 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-03-passo-a-passo-catalogo.md`.

## Antes de começar

Certifique-se de que as imagens `todo-backend:v1` e `todo-frontend:v1` da Aula 02 ainda existem:

```bash
docker images
```

---

## Parte 1 — Comprovando a Efemeridade

Suba um container PostgreSQL sem volume:

```bash
docker run -d --name teste-db -e POSTGRES_PASSWORD=teste123 -p 5434:5432 postgres:16
```

Aguarde alguns segundos e conecte via DBeaver (host `localhost`, porta `5434`, usuário `postgres`, senha `teste123`). Crie uma tabela simples e insira um registro:

```sql
CREATE TABLE prova (id SERIAL PRIMARY KEY, nome TEXT);
INSERT INTO prova (nome) VALUES ('este dado vai sumir');
```

Agora remova o container:

```bash
docker stop teste-db
docker rm teste-db
```

Suba um novo container com o mesmo nome:

```bash
docker run -d --name teste-db -e POSTGRES_PASSWORD=teste123 -p 5434:5432 postgres:16
```

Conecte de novo pelo DBeaver e tente consultar a tabela `prova`. Ela não existe mais — os dados se perderam junto com o container anterior.

Remova este container de teste:

```bash
docker stop teste-db
docker rm teste-db
```

---

## Parte 2 — Criando um Volume Persistente

Crie um volume nomeado:

```bash
docker volume create todo-db-data
```

Suba o PostgreSQL usando esse volume:

```bash
docker run -d --name todo-db \
  -e POSTGRES_DB=todo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v todo-db-data:/var/lib/postgresql/data \
  -p 5434:5432 \
  postgres:16
```

Conecte pelo DBeaver e crie uma tabela de teste, igual ao passo anterior.

Remova o container (sem remover o volume):

```bash
docker stop todo-db
docker rm todo-db
```

Suba o container de novo, usando o mesmo volume:

```bash
docker run -d --name todo-db \
  -e POSTGRES_DB=todo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v todo-db-data:/var/lib/postgresql/data \
  -p 5434:5432 \
  postgres:16
```

Consulte a tabela de teste novamente. Desta vez os dados devem estar lá.

---

## Parte 3 — Criando uma Rede e Conectando o Backend

Crie a rede do projeto:

```bash
docker network create todo-network
```

Remova o container `todo-db` atual (o volume continua guardando os dados):

```bash
docker stop todo-db
docker rm todo-db
```

Suba o PostgreSQL novamente, agora dentro da rede:

```bash
docker run -d --name db \
  --network todo-network \
  -e POSTGRES_DB=todo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -v todo-db-data:/var/lib/postgresql/data \
  postgres:16
```

Observe que este container não tem `-p` — não precisamos acessá-lo diretamente do host, apenas o backend vai falar com ele.

Suba o backend na mesma rede, com as variáveis de ambiente apontando para o banco:

```bash
docker run -d --name todo-backend \
  --network todo-network \
  -e POSTGRES_DB=todo \
  -e POSTGRES_USER=postgres_user \
  -e POSTGRES_PASSWORD=postgres_pass \
  -e POSTGRES_HOST=db \
  -e POSTGRES_PORT=5432 \
  -e SECRET_KEY=your-secret-key-here \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -p 8000:8000 \
  todo-backend:v1
```

Repare que `POSTGRES_HOST=db` usa o **nome do container**, não um IP.

> **Atenção:** diferente da Aula 02 (que usava `--env-file .env`, carregando todas as variáveis de uma vez), aqui estamos passando cada variável individualmente com `-e`. Isso significa que **toda** variável que o Django exige precisa aparecer na lista — inclusive `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS`, que não têm relação com rede/banco mas são obrigatórias no `core/settings.py` (via `pydantic-settings`). Se esquecer alguma, o container sobe e morre imediatamente (`docker ps -a` mostra `Exited`), e `docker exec` reclama que o container não está rodando. Para investigar esse tipo de falha, use `docker logs todo-backend`.

---

## Parte 4 — Rodando as Migrations

Execute as migrations do Django dentro do container em execução:

```bash
docker exec -it todo-backend uv run python manage.py migrate
```

Acesse: `http://localhost:8000/api/tasks/`

---

## Parte 5 — Inspecionando os Containers

Veja os detalhes de rede e variáveis de ambiente do backend:

```bash
docker inspect todo-backend
```

Procure pelas seções `NetworkSettings` e `Env` no resultado.

---

## Checklist final do dia

- [ ] Efemeridade comprovada (dados perdidos sem volume)
- [ ] Volume nomeado criado e persistência comprovada
- [ ] Rede `todo-network` criada
- [ ] Container do banco rodando sem porta exposta para o host
- [ ] Backend conectado ao banco pelo nome do container
- [ ] Migrations executadas com sucesso

---

## Material de apoio

- Docker Volumes — documentação oficial: https://docs.docker.com/engine/storage/volumes/
- Docker Networks — documentação oficial: https://docs.docker.com/engine/network/
- docker inspect — referência: https://docs.docker.com/reference/cli/docker/inspect/
