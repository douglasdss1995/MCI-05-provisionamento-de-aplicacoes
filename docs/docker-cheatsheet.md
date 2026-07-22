# Docker Cheatsheet — Comandos Essenciais

## Docker Container

```bash
docker container ls              # lista containers rodando
docker container ls -a           # lista todos, incluindo parados
docker run -d --name app image   # cria e inicia um container em background
docker start container_name      # inicia um container parado
docker stop container_name       # para um container rodando (graceful shutdown)
docker restart container_name    # para e inicia novamente (stop + start)
docker exec -it container_name bash   # entra no container com shell interativo (bash)
docker exec -it container_name sh     # idem, para imagens sem bash (ex.: nginx:alpine)
docker logs container_name       # mostra logs
docker logs -f container_name    # segue logs em tempo real (follow)
docker logs --tail 100 container_name # mostra só as últimas 100 linhas
docker rm container_name         # remove container parado
docker rm -f container_name      # força remoção mesmo rodando
```

**Ponto de atenção:** `docker stop` manda SIGTERM e espera 10s antes de matar com SIGKILL. Se a aplicação não trata SIGTERM, ela morre sem limpar conexões abertas com banco, filas, etc. Isso vira conexão órfã no Postgres ou mensagem perdida no Redis em produção.

## Docker Image

```bash
docker images                    # lista imagens locais
docker build -t nome:tag .       # constrói imagem a partir do Dockerfile no diretório atual
docker pull nome:tag             # baixa imagem do registry
docker rmi nome:tag              # remove imagem
docker image prune               # remove imagens dangling (sem tag, órfãs de build)
```

## Docker Network

```bash
docker network ls                        # lista networks
docker network create nome               # cria uma network (bridge por padrão)
docker network inspect nome              # mostra detalhes e containers conectados
docker network connect nome container    # conecta um container já existente à network
docker network rm nome                   # remove uma network não usada
```

## Docker Volume

```bash
docker volume ls               # lista volumes
docker volume create nome      # cria um volume nomeado
docker volume inspect nome     # mostra detalhes, incluindo caminho no host
docker volume rm nome          # remove um volume não usado
```

**Ponto de atenção:** volumes nomeados (ex.: `static_volume` compartilhado entre backend e Nginx) não são removidos por `docker compose down` sozinho — é preciso `docker compose down -v`. Rodar sem `-v` por hábito é o motivo mais comum de "os estáticos antigos ainda aparecem" depois de recriar a stack.

## Monitoramento

```bash
docker stats                   # uso de CPU/memória/rede em tempo real, todos os containers
docker stats container_name    # idem, só de um container
docker top container_name      # processos rodando dentro do container
```

## Limpeza (usar com cautela)

```bash
docker container prune           # remove todos os containers parados
docker system prune              # remove containers parados, imagens dangling, redes não usadas e cache de build
docker system prune -a           # remove TUDO não usado, incluindo imagens sem container associado
```

`docker system prune -a` é destrutivo. Em máquina compartilhada, confirme com quem mais usa aquele Docker antes de rodar.

## Docker Compose

```bash
docker compose up -d              # sobe os serviços definidos, em background
docker compose up -d --build      # builda as imagens e sobe, em um único comando
docker compose build              # constrói as imagens definidas no compose
docker compose ps                 # status dos serviços do compose
docker compose logs -f servico    # logs de um serviço específico
docker compose exec servico sh    # shell interativo dentro de um serviço rodando
docker compose restart servico    # reinicia um serviço específico
docker compose down               # para e remove containers do compose
docker compose down -v            # idem, e também remove os volumes nomeados
```

**Ambiente com `shared-network`:** como Postgres e Redis rodam localmente e não entram no compose, verifique sempre se a network existe antes do `up`:

```bash
docker network ls | grep shared-network
```

Se a network não existir, o `up` pode falhar de forma pouco clara, levando a debugar a aplicação achando que é bug de código quando na verdade é infraestrutura.
