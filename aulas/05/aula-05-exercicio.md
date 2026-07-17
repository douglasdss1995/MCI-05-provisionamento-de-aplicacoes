# Exercício E5 — Variáveis de Ambiente, Segredos e Boas Práticas

> Exercício avaliado do dia — Catálogo de Filmes. Baseado no seu próprio passo
> a passo (`aula-05-passo-a-passo-catalogo.md`).

## Objetivo

Demonstrar que você sabe extrair segredos e configurações do
`docker-compose.yml` para um arquivo `.env`, documentar essas variáveis num
`.env.example`, manter o `.env` fora do controle de versão, e ler essas
variáveis no Django através do `pydantic-settings`.

## O que entregar

- [ ] `.env.example` documentado em português (sem valores reais de senha/chave)
- [ ] `.gitignore` atualizado, com `.env` fora do controle de versão
- [ ] `docker-compose.yml` atualizado para usar `env_file: - .env` em vez de variáveis inline
- [ ] `backend/core/settings.py` (ou equivalente) lendo as variáveis via `pydantic-settings`
- [ ] `.env.production` como referência de ambiente de produção (não usado, só para comparação)

## Critério de aceite

```bash
git status
```

O arquivo `.env` **não** deve aparecer na saída. Com o `.env` presente na
máquina, `docker compose up -d --build` deve subir a stack normalmente, lendo
todas as variáveis do arquivo.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar), assim como prints dos containers funcionando 
na atividade **5** criada no Classroom correspondente a esta aula.
