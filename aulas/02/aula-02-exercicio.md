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

## Critérios de avaliação

| Critério         | Peso | O que é avaliado neste exercício                                                                                                                                              |
| ---------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Funcionalidade   | 50%  | As duas imagens buildam sem erro; frontend e backend conversam através da rede Docker                                                                                         |
| Boas práticas    | 30%  | `.dockerignore` completo (sem `.env`/`.venv`/cache); imagem base `python:3.12-slim`; Dockerfile do frontend é multi-stage (não expõe as ferramentas de build na imagem final) |
| Entrega no prazo | 20%  | Enviado até o prazo combinado em aula                                                                                                                                         |

## Entrega

Envie o link do repositório (ou compacte a pasta `catalogo/`, conforme
orientação do professor no dia).
