# Exercício E4 — Docker Compose: Stack Completa

> Exercício avaliado do dia — Catálogo de Filmes. Baseado no seu próprio passo
> a passo (`aula-04-passo-a-passo-catalogo.md`).

## Objetivo

Demonstrar que você sabe orquestrar banco de dados, backend e frontend num
único `docker-compose.yml`, usando `healthcheck` e `depends_on` para garantir
que o backend só suba depois que o banco estiver pronto.

## O que entregar

- [ ] `docker-compose.yml` na raiz do projeto do Catálogo

## Critério de aceite

```bash
docker compose up -d
docker compose ps
```

Todos os serviços devem subir com status `running` (o banco como `healthy`).
O frontend deve carregar em `localhost:4300` (ou na porta combinada em aula) e
listar filmes vindos do backend.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar), assim como prints dos containers funcionando 
na atividade **4** criada no Classroom correspondente a esta aula.