# Exercício E8 — Makefile, Logs e Monitoramento

> Exercício avaliado do dia — Catálogo de Filmes. Baseado no seu próprio passo
> a passo (`aula-08-passo-a-passo-catalogo.md`).

## Objetivo

Demonstrar que você sabe automatizar os comandos do dia a dia do projeto num
`Makefile`, e que sabe observar o consumo de recursos da stack em execução.

## O que entregar

- [ ] `Makefile` na raiz do projeto, com indentação por **TAB** e ao menos os alvos `build`, `up`, `down`, `migrate`, `logs`, `shell`

## Critério de aceite

```bash
make help
make build
make up
make migrate
make logs
make shell
```

Todos os alvos devem rodar sem erro. `make help` deve listar os alvos
disponíveis com uma breve descrição de cada um.

## Entrega

Envie o que foi definido na sessão [O que entregar](#o-que-entregar), assim como prints dos containers e aplicação funcionando 
na atividade **8** criada no Classroom correspondente a esta aula.