# Exercício E6 — Nginx: Proxy Reverso, Estáticos e Gateway Único

> Exercício avaliado do dia — Catálogo de Filmes.

## Objetivo

Demonstrar que você sabe colocar um Nginx na frente da stack como gateway
único, roteando para o frontend, para a API do backend e para os arquivos
estáticos do Django Admin, sem expor as portas internas de backend/frontend
para o host.

## O que entregar

Arquivos:

- [ ] `nginx/nginx.conf` (gateway único, com rotas para `/`, `/api/` e `/admin/`)
- [ ] `backend/entrypoint.sh` (executável, rodando `collectstatic` antes do Gunicorn)
- [ ] `docker-compose.yml` atualizado (serviço `nginx` novo; `backend` e `frontend` sem `ports:`; volume de estáticos compartilhado)

Prints:

- [ ] Retorno do comando: `docker compose up -d --build`
- [ ] Retorno do comando: `docker ps`
- [ ] Aplicação funcionando com filmes cadastrados.
- [ ] Aplicação funcionando com filmes cadastrados.
- [ ] Django Admin

A aplicação completa deve ficar acessível **só** pela porta do Nginx
(`localhost` ou a porta combinada em aula). O Django Admin deve carregar
com o CSS funcionando (prova de que os estáticos estão sendo servidos
corretamente pelo Nginx).

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar) no Classroom correspondente a esta aula 06.
