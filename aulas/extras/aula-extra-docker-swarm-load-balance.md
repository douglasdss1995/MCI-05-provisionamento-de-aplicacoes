# Aula Extra — Docker Swarm e Load Balancing entre Serviços

> **Conteúdo bônus, fora da grade avaliada.** O Dia 08 já citou Docker Swarm como assunto "para estudar depois" — esta aula é esse próximo passo, na prática. Ela parte do estado da Lista de Tarefas ao final da Aula 08 (`aulas/08/todo/`) e não depende de nenhuma aula posterior.

## Antes de começar

Entre em `aulas/08/todo/` (ou na sua cópia equivalente do projeto) e confirme que a stack normal, via Docker Compose, ainda sobe sem erro:

```bash
docker compose up -d
docker compose ps
```

Acesse `http://localhost/` e confirme que a aplicação responde. Depois, derrube a stack — o Swarm vai precisar da porta 80 livre:

```bash
docker compose down
```

---

## Parte 1 — O que é Docker Swarm

Até aqui, `docker compose up` sempre rodou os containers em uma única máquina, sem nenhum mecanismo automático de recuperação: se o container do `backend` morresse, ele ficaria morto até alguém rodar `docker compose up` de novo.

**Docker Swarm** é o orquestrador de containers nativo do Docker. Ele transforma uma ou mais máquinas (chamadas de *nodes*) em um cluster, e some com um conjunto de garantias que o Compose sozinho não dá:

- **Réplicas**: um mesmo serviço pode rodar em várias cópias idênticas (*réplicas*) ao mesmo tempo.
- **Load balancing automático**: requisições para um serviço são distribuídas entre suas réplicas, sem nenhuma configuração manual de round-robin.
- **Self-healing**: se uma réplica morre, o Swarm sobe outra no lugar automaticamente, para manter o número de réplicas declarado.
- **Rede overlay**: uma rede virtual que conecta containers mesmo que estejam rodando em nodes (máquinas) diferentes.
- **Routing mesh**: qualquer node do cluster que receber uma requisição numa porta publicada sabe redirecioná-la para uma réplica saudável do serviço certo, esteja ela nesse node ou em outro.

Nesta aula você vai rodar um cluster de **um único node** (sua própria máquina) — o suficiente para ver réplicas, self-healing e load balancing funcionando, sem precisar de várias máquinas.

> **Atenção:** `docker stack deploy` (o comando usado com Swarm) lê um arquivo no mesmo formato do `docker-compose.yml`, mas **ignora alguns campos** que só fazem sentido para o Compose isolado — o principal é `build:`. Um `docker stack deploy` nunca constrói uma imagem a partir de um Dockerfile: ele só sabe usar imagens já prontas (`image:`). Isso muda como vamos preparar as imagens do backend e do frontend nesta aula.

---

## Parte 2 — Inicializando o Swarm

Transforme sua máquina em um node gerente (*manager*) de um cluster Swarm:

```bash
docker swarm init
```

Confirme que o node aparece, com o papel de `Leader` (o único manager do cluster, por enquanto):

```bash
docker node ls
```

---

## Parte 3 — Construindo as Imagens Localmente

Como o Swarm não builda a partir de `build:`, construa as imagens do backend e do frontend manualmente, com uma tag fixa:

```bash
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

Confirme que as duas imagens existem localmente:

```bash
docker images | grep todo-
```

Como o cluster tem um único node, essas imagens já estão disponíveis para o Swarm usar — em um cluster com vários nodes, seria necessário publicá-las em um registry (como o `ghcr.io` da Aula 07) para que todos os nodes conseguissem baixá-las.

---

## Parte 4 — Distribuindo o `nginx.conf` como Docker Config

Até aqui, o `nginx/nginx.conf` sempre chegou ao container por um bind mount (`./nginx/nginx.conf:/etc/nginx/conf.d/default.conf` no `docker-compose.yml`). Isso funciona porque o Compose sempre roda no mesmo node onde o arquivo existe no disco.

Em um cluster Swarm, uma réplica do serviço `nginx` pode ser agendada em qualquer node — inclusive um que nunca teve esse arquivo copiado para o disco. Por isso o Swarm tem seu próprio mecanismo para distribuir arquivos de configuração a qualquer node do cluster: **Docker Configs**.

Crie o Config a partir do arquivo já existente:

```bash
docker config create todo_nginx_conf nginx/nginx.conf
```

Confirme que foi criado:

```bash
docker config ls
```

> Um Config, uma vez criado, é imutável — se precisar alterar o `nginx.conf`, é preciso criar um novo Config com outro nome (ex.: `todo_nginx_conf_v2`) e atualizar o serviço para usá-lo. É um design proposital do Swarm, para garantir que toda réplica de um serviço sempre usa exatamente a mesma versão do arquivo.

---

## Parte 5 — Criando o `docker-stack.yml`

Um arquivo de stack usa a mesma sintaxe do `docker-compose.yml`, mas com um bloco `deploy:` por serviço, que só o Swarm interpreta (o Compose isolado o ignora silenciosamente). Crie o arquivo `docker-stack.yml`, na raiz do projeto, ao lado do `docker-compose.yml` — **os dois arquivos continuam existindo lado a lado**, para dois propósitos diferentes:

```yaml
# docker-stack.yml
# Descreve a mesma aplicacao do docker-compose.yml, mas para rodar
# como uma stack no Docker Swarm, com replicas e load balancing.
# Diferente do docker-compose.yml, este arquivo nunca builda imagem
# (sem "build:") - so usa imagens ja prontas, por isso "image:" aqui
# aponta para as imagens construidas na Parte 3.

services:
  db:
    image: postgres:16
    volumes:
      - todo-db-data:/var/lib/postgresql/data
    env_file:
      - .env
    networks:
      - app_network
    deploy:
      replicas: 1
      # Fixa o Postgres sempre no node gerente: o volume "todo-db-data"
      # e local a um node especifico, entao a replica do banco precisa
      # sempre subir no mesmo lugar onde os dados ja existem no disco.
      # Um Postgres com varias replicas nao replica dados sozinho -
      # exigiria uma solucao de replicacao de banco, fora do escopo aqui.
      placement:
        constraints:
          - node.role == manager

  backend:
    image: todo-backend:latest
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
    networks:
      - app_network
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure

  frontend:
    image: todo-frontend:latest
    networks:
      - app_network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - static_volume:/app/staticfiles
    configs:
      - source: todo_nginx_conf
        target: /etc/nginx/conf.d/default.conf
    networks:
      - app_network
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure

networks:
  # Redes overlay conectam containers entre nodes diferentes do cluster -
  # a rede padrao (bridge) do Compose so funciona dentro de um unico node
  app_network:
    driver: overlay

configs:
  todo_nginx_conf:
    external: true

volumes:
  todo-db-data:
  static_volume:
```

> **Nota:** `depends_on` não aparece mais aqui de propósito — o Swarm não espera um serviço ficar "healthy" antes de subir outro, então essa condição (`condition: service_healthy`, usada no `docker-compose.yml`) simplesmente não tem efeito em uma stack. Na prática, isso significa que o `backend` pode tentar subir antes do Postgres estar pronto para aceitar conexões; a `restart_policy: on-failure` cobre esse caso — o Swarm reinicia a réplica que falhou até ela conseguir conectar.

---

## Parte 6 — Fazendo o Deploy da Stack

```bash
docker stack deploy -c docker-stack.yml todo
```

O nome `todo` no final é o nome da *stack* — o Swarm usa esse nome como prefixo de cada serviço (`todo_db`, `todo_backend`, `todo_frontend`, `todo_nginx`).

---

## Parte 7 — Verificando Réplicas e Testando o Load Balancing

Liste os serviços da stack e quantas réplicas de cada estão de pé:

```bash
docker stack services todo
```

Veja o detalhe de cada réplica (em qual node está, se está rodando):

```bash
docker stack ps todo
```

Para ver o load balancing acontecendo, abra dois terminais.

No primeiro, acompanhe os logs do serviço `backend` (não de um container específico — do serviço inteiro, que agrega os logs de todas as réplicas):

```bash
docker service logs -f todo_backend
```

No segundo terminal, faça várias requisições seguidas à API:

```bash
for i in $(seq 1 10); do curl -s http://localhost/api/tasks/ > /dev/null; done
```

No terminal dos logs, repare que as linhas de log vêm de containers diferentes (o prefixo de cada linha traz um ID de container distinto) — é o Swarm distribuindo as 10 requisições entre as 3 réplicas do `backend`, sem que a aplicação precise saber que existe mais de uma réplica.

---

## Parte 8 — Escalando um Serviço em Tempo Real

Aumente o número de réplicas do backend sem recriar a stack inteira:

```bash
docker service scale todo_backend=5
```

Confirme que agora existem 5 réplicas rodando:

```bash
docker stack ps todo
```

---

## Parte 9 — Atualizando uma Imagem sem Downtime (Rolling Update)

Depois de alterar o código do backend e gerar uma nova imagem (`docker build -t todo-backend:latest ./backend` de novo), aplique a atualização ao serviço:

```bash
docker service update --image todo-backend:latest todo_backend
```

O Swarm troca as réplicas antigas pelas novas **uma de cada vez**, mantendo o serviço disponível durante toda a atualização — diferente de um `docker compose up -d --build`, que recria o container de uma vez só.

---

## Parte 10 — Encerrando

Remova a stack:

```bash
docker stack rm todo
```

Se quiser sair do modo Swarm completamente e voltar a usar só o Compose:

```bash
docker swarm leave --force
```

A partir daqui, volte a subir a aplicação normalmente com `docker compose up -d`.

---

## Checklist final

- [ ] `docker swarm init` executado, node aparece como `Leader`
- [ ] Imagens `todo-backend:latest` e `todo-frontend:latest` construídas localmente
- [ ] Config `todo_nginx_conf` criado a partir do `nginx/nginx.conf`
- [ ] `docker-stack.yml` criado, com `deploy.replicas` para `backend` (3) e `frontend` (2), e `db` fixado no manager (`placement.constraints`)
- [ ] Rede `app_network` do tipo `overlay` declarada
- [ ] `docker stack deploy -c docker-stack.yml todo` executado com sucesso
- [ ] `docker stack services todo` mostra todas as réplicas desejadas rodando
- [ ] Load balancing observado nos logs do serviço `backend` ao repetir requisições
- [ ] `docker service scale todo_backend=5` testado
- [ ] Stack removida com `docker stack rm todo` ao final

---

## Material de apoio

- Docker Swarm — visão geral: https://docs.docker.com/engine/swarm/
- Docker — `docker stack deploy`: https://docs.docker.com/engine/reference/commandline/stack_deploy/
- Docker — `docker service`: https://docs.docker.com/engine/reference/commandline/service/
- Docker — rede overlay: https://docs.docker.com/network/drivers/overlay/
- Docker — Configs: https://docs.docker.com/engine/swarm/configs/
- Docker — Compose file reference (campos suportados em `deploy:`): https://docs.docker.com/compose/compose-file/deploy/
