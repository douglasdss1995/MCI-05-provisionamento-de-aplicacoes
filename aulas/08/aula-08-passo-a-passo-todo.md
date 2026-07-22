# Aula 08 — Passo a Passo do Aluno

> **Demonstração do professor — Lista de Tarefas (Todo).** O professor constrói esta parte ao vivo; acompanhe em paralelo, no seu próprio ambiente. Depois que terminarmos por aqui, é a sua vez de repetir sozinho o mesmo padrão na segunda aplicação do curso — veja `aula-08-passo-a-passo-catalogo.md`.

## Antes de começar

Confirme que a stack completa sobe corretamente:

```bash
docker compose up -d
docker compose ps
```

---

## Parte 1 — Verificando o make

Confirme que o `make` está disponível no seu WSL:

```bash
make --version
```

Se não estiver instalado:

```bash
sudo apt install make -y
```

---

## Parte 2 — Criando o Makefile

Na raiz do projeto, crie o arquivo `Makefile` (sem extensão).

**Atenção:** a indentação de cada comando abaixo do alvo precisa ser feita com **TAB**, nunca com espaços. A maioria dos editores de texto faz essa conversão automaticamente ao detectar um Makefile, mas vale confirmar.

```makefile
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
```

---

## Parte 3 — Testando os Alvos

Liste os comandos disponíveis:

```bash
make help
```

Você deve ver uma lista com o nome de cada alvo e sua descrição.

Teste o alvo de build:

```bash
make build
```

Suba a stack:

```bash
make up
```

Rode as migrations:

```bash
make migrate
```

Acompanhe os logs:

```bash
make logs
```

Pressione `Ctrl + C` para parar de acompanhar. Acesse o shell do backend:

```bash
make shell
```

Dentro do container, confirme que está no lugar certo:

```bash
pwd
exit
```

Encerre a stack:

```bash
make down
```

---

## Parte 4 — Adicionando Log Estruturado (Opcional)

Se o projeto do curso já usa `structlog`, procure por um trecho de código que usa `print()` e substitua por um log estruturado:

```python
import structlog

logger = structlog.get_logger()

# Antes:
# print(f"Tarefa criada: {task.id}")

# Depois:
logger.info("task_created", task_id=task.id, title=task.title)
```

---

## Parte 5 — Observando o Uso de Recursos

Com a stack no ar, abra um novo terminal e execute:

```bash
docker stats
```

Observe o consumo de CPU e memória de cada container. Pressione `Ctrl + C` para sair.

---

## Checklist final do dia

- [ ] `Makefile` criado com indentação correta (TAB)
- [ ] `make help` lista todos os alvos com descrição
- [ ] `make build` e `make up` funcionam sem erro
- [ ] `make migrate` executa as migrations corretamente
- [ ] `make logs` e `make shell` funcionam como esperado
- [ ] `docker stats` testado com a stack no ar

---

## Material de apoio

- GNU Make — manual oficial: https://www.gnu.org/software/make/manual/make.html
- structlog — documentação oficial: https://www.structlog.org/
- Docker — docker stats: https://docs.docker.com/reference/cli/docker/container/stats/
- Prometheus — visão geral: https://prometheus.io/docs/introduction/overview/
- Grafana — visão geral: https://grafana.com/docs/grafana/latest/introduction/
