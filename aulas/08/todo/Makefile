# Makefile
# Automatiza os comandos mais usados no dia a dia do projeto

.PHONY: build up down migrate logs shell help

build: ## Constroi as imagens da stack
	docker compose build

up: ## Sobe a stack em segundo plano
	docker compose up -d

down: ## Encerra a stack
	docker compose down

migrate: ## Executa as migrations do Django
	docker compose exec backend uv run python manage.py migrate

logs: ## Acompanha os logs de todos os servicos
	docker compose logs -f

shell: ## Abre um shell dentro do container do backend
	docker compose exec backend sh

help: ## Lista os comandos disponiveis e suas descricoes
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'
