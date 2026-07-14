# Docker Cheatsheet — Comandos Essenciais

## Docker Container

```bash
docker container ls              # lista containers rodando
docker container ls -a           # lista todos, incluindo parados
docker container rm -f container_name # força remoção mesmo rodando
docker run -d --name app image   # cria e inicia um container em background
docker start container_name      # inicia um container parado
docker stop container_name       # para um container rodando (graceful shutdown)
docker restart container_name    # reinicia
docker exec -it container_name bash   # entra no container com shell interativo
docker logs container_name       # mostra logs
docker logs -f container_name    # segue logs em tempo real (follow)
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

## Limpeza (usar com cautela)

```bash
docker container prune           # remove todos os containers parados
docker system prune              # remove containers parados, imagens dangling, redes não usadas
docker system prune -a           # remove TUDO não usado, incluindo imagens sem container associado
```

`docker system prune -a` é destrutivo. Em máquina compartilhada, confirme com quem mais usa aquele Docker antes de rodar.

## Docker Compose

```bash
docker compose up -d              # sobe os serviços definidos, em background
docker compose down               # para e remove containers do compose
docker compose logs -f servico    # logs de um serviço específico
docker compose ps                 # status dos serviços do compose
```

**Ambiente com `shared-network`:** como Postgres e Redis rodam localmente e não entram no compose, verifique sempre se a network existe antes do `up`:

```bash
docker network ls | grep shared-network
```

Se a network não existir, o `up` pode falhar de forma pouco clara, levando a debugar a aplicação achando que é bug de código quando na verdade é infraestrutura.