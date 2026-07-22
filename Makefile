# Makefile
# Automatiza os comandos mais usados no dia a dia com Git

.PHONY: help status add commit push push-force pull fetch log branch checkout diff stash stash-pop rebase rebase-continue rebase-abort

help: ## Lista os comandos disponiveis e suas descricoes
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'

status: ## Mostra o status do repositorio
	git status

add: ## Adiciona todas as alteracoes ao stage
	git add .

commit: ## Cria um commit com a mensagem informada (make commit m="mensagem")
	git commit -m "$(m)"

push: ## Envia os commits para o repositorio remoto
	git push

push-force: ## Forca o push com seguranca, abortando se o remoto mudou (--force-with-lease)
	git push --force-with-lease

pull: ## Atualiza o repositorio local com o remoto
	git pull

fetch: ## Busca atualizacoes do remoto sem aplicar
	git fetch --all

log: ## Mostra o historico de commits de forma resumida
	git log --oneline --graph --decorate --all

branch: ## Lista todas as branches, locais e remotas
	git branch -a

checkout: ## Troca de branch (make checkout b="nome-da-branch")
	git checkout $(b)

diff: ## Mostra as diferencas ainda nao commitadas
	git diff

stash: ## Guarda as alteracoes atuais temporariamente
	git stash

stash-pop: ## Restaura as alteracoes guardadas pelo stash
	git stash pop

rebase: b ?= main
rebase: ## Rebasa a branch atual sobre outra (make rebase b="nome-da-branch", padrao: main)
	git rebase $(b)

rebase-continue: ## Continua um rebase apos resolver conflitos
	git rebase --continue

rebase-abort: ## Cancela um rebase em andamento e volta ao estado anterior
	git rebase --abort
