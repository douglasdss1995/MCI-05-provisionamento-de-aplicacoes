# Exercício E7 — CI/CD com GitHub Actions

> Exercício avaliado do dia — Catálogo de Filmes.

## Objetivo

Demonstrar que você sabe montar um pipeline de integração contínua que roda
lint e testes automatizados contra um banco de dados de serviço, e que só
publica a imagem no `ghcr.io` depois que o pipeline passar.

## O que entregar

- [ ] `.github/workflows/ci.yml`
- [ ] Link do repositório criado
- [ ] Print da pipeline concluída com sucesso.

O pipeline deve aparecer **verde** na aba Actions do GitHub após um `push`
para `main` (ou `pull_request`, conforme o gatilho configurado), executando
`ruff check`, `manage.py check`, `makemigrations --check --dry-run`,
`manage.py migrate` e `pytest` contra o serviço `postgres` definido no
workflow. Após o merge em `main`, a imagem publicada deve aparecer em
`ghcr.io/<seu-usuario>/<repositório>/catalogo-backend`.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar) no Classroom correspondente a esta aula 07.