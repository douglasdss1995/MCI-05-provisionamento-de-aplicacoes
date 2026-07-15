# Exercício E3 — Volumes, Redes e Comunicação entre Containers

> Exercício avaliado do dia — Catálogo de Filmes. Baseado no seu próprio passo
> a passo (`aula-03-passo-a-passo-catalogo.md`).

## Objetivo

Demonstrar que você entende a efemeridade de containers, sabe criar um volume
nomeado para persistir os dados do banco, e sabe conectar o backend ao banco
através de uma rede Docker customizada usando o **nome do container** (não
IP), sem expor a porta do banco para o host.

## O que entregar

Esta aula não produz nenhum arquivo novo no projeto — todos os artefatos são
objetos Docker (volume, rede, containers). A entrega é **evidência de
execução**, não um arquivo:

- [ ] Print ou saída de `docker volume ls` mostrando o volume `catalogo-db-data`
- [ ] Print ou saída de `docker network inspect catalogo-network` mostrando o banco e o backend conectados
- [ ] Print ou saída de `docker ps` mostrando o container do banco **sem** coluna `PORTS` publicada para o host
- [ ] Print ou saída de `docker exec ... uv run python manage.py migrate` rodando com sucesso dentro do container do backend

## Critério de aceite

```bash
docker volume ls | grep catalogo-db-data
docker network inspect catalogo-network
docker ps --filter name=catalogo-db
```

O container do banco deve aparecer rodando **sem** `-p`/porta publicada, e o
backend deve conseguir migrar e responder em `/api/movies/` usando
`POSTGRES_HOST` igual ao nome do container do banco.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar), assim como prints dos containers funcionando 
na atividade **3** criada no Classroom correspondente a esta aula.
