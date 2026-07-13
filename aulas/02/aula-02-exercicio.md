# Exercício E2 — Dockerfiles para Django e Angular

> Exercício avaliado do dia — Catálogo de Filmes. Baseado no seu próprio passo
> a passo (`aula-02-passo-a-passo-catalogo.md`).

## Objetivo

Demonstrar que você conseguiu criar, um `Dockerfile` para uma aplicação
Django e um `Dockerfile` multi-stage para uma aplicação Angular, e conectar o
backend containerizado a um banco de dados PostgreSQL através de uma rede
Docker criada por você.

## O que entregar

- [ ] `backend/Dockerfile`
- [ ] `backend/.dockerignore` (sem `.env`, `.venv`, cache)
- [ ] `frontend/Dockerfile` (multi-stage: build com `node:20-alpine`, runtime com `nginx:alpine`)
- [ ] `frontend/nginx.conf` (com `proxy_pass` de `/api/` para o backend e `try_files` para o roteamento do Angular)

## Critério de aceite

```bash
docker build -t catalogo-backend:v1 backend/
docker build -t catalogo-frontend:v1 frontend/
```

As duas imagens devem construir sem erro. Subindo os dois containers na mesma
rede Docker (como no passo a passo), o catálogo de filmes deve carregar em
`localhost:4300` (ou na porta combinada em aula) e listar filmes vindos do
backend em `/api/movies/`.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar), assim como prints dos containers funcionando 
na atividade **2** criada no Classroom correspondente a esta aula.
