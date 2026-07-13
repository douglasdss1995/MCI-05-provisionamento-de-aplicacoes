# Aula 01 — Passo a Passo do Aluno

## Antes de começar

Você vai precisar de:

- Windows 11 com WSL2 habilitado
- Acesso à internet
- Uma conta no GitHub (crie em https://github.com se ainda não tiver)

---

## Parte 1 — Verificando o WSL2

Abra o PowerShell como administrador e confirme a versão do WSL instalada.

```powershell
wsl --version
```

Se o comando não for reconhecido, o WSL2 não está instalado. Avise o professor antes de continuar.

Liste as distribuições instaladas:

```powershell
wsl --list --verbose
```

Você deve ver uma distribuição Ubuntu com a versão 2 na coluna `VERSION`. Se estiver na versão 1, será necessário atualizar — peça ajuda ao professor.

---

## Parte 2 — Acessando o Ubuntu

Abra o terminal do Ubuntu (procure "Ubuntu" no menu iniciar, ou digite `wsl` no PowerShell).

Atualize os pacotes do sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

Este comando pode levar alguns minutos na primeira execução.

---

## Parte 3 — Instalando o Docker Engine

Importante: **não instale o Docker Desktop**. Vamos usar apenas o Docker Engine, diretamente no WSL2.

Se você já tem o Docker Desktop instalado, desinstale-o pelo Windows antes de continuar (Painel de Controle → Programas → Desinstalar).

Execute os comandos abaixo, um por vez, dentro do Ubuntu:

```bash
# Remove versões antigas, se existirem
sudo apt remove docker docker-engine docker.io containerd runc

# Instala dependências necessárias
sudo apt install ca-certificates curl gnupg -y

# Adiciona a chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adiciona o repositório do Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instala o Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

Adicione seu usuário ao grupo `docker` para não precisar de `sudo` em todo comando:

```bash
sudo usermod -aG docker $USER
```

Feche o terminal e abra novamente para que a mudança de grupo tenha efeito.

Confirme que o Docker está funcionando:

```bash
docker --version
docker run hello-world
```

Se aparecer uma mensagem de boas-vindas do Docker, está tudo certo.

---

## Parte 4 — Instalando o uv

O `uv` é o gerenciador de dependências Python que vamos usar no curso.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirme a instalação:

```bash
uv --version
```

---

## Parte 5 — Instalando o Git

Normalmente já vem instalado no Ubuntu, mas confirme:

```bash
git --version
```

Se não estiver instalado:

```bash
sudo apt install git -y
```

Configure seu nome e e-mail (use os mesmos dados da sua conta do GitHub):

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

---

## Parte 6 — Instalando o DBeaver

O DBeaver roda no Windows, não no WSL. Baixe o instalador em:

https://dbeaver.io/download/

Instale normalmente como qualquer programa do Windows.

---

## Parte 7 — Clonando o repositório do curso

Ainda dentro do Ubuntu (WSL), clone o repositório com os materiais do curso:

```bash
git clone https://github.com/douglasdss1995/MCI-05-provisionamento-de-aplicacoes
cd MCI-05-provisionamento-de-aplicacoes
```

---

## Parte 8 — Baixando as imagens Docker do curso

Dentro da pasta do repositório, execute o script que baixa todas as imagens que vamos usar durante o curso. Isso evita que você precise baixar imagens durante as próximas aulas.

```bash
chmod +x pull_images.sh
./pull_images.sh
```

Este script baixa as seguintes imagens:

- `python:3.12-slim`
- `node:20-alpine`
- `nginx:alpine`
- `postgres:16`
- `alpine:latest`

Confirme que todas foram baixadas:

```bash
docker images
```

---

## Parte 9 — Testando os Containers Base (Nginx e PostgreSQL)

Com as imagens já baixadas na Parte 8, vamos confirmar que Docker, Nginx e PostgreSQL funcionam corretamente antes de começar a programar nas próximas aulas.

### Subindo um Nginx de teste

```bash
docker run -d --name meu-nginx -p 8080:80 nginx:alpine
```

Acesse no navegador:

```
http://localhost:8080
```

Você deve ver a página de boas-vindas padrão do Nginx. Remova o container de teste:

```bash
docker stop meu-nginx
docker rm meu-nginx
```

### Subindo um PostgreSQL de teste

```bash
docker run -d --name meu-postgres -e POSTGRES_PASSWORD=etech123 -p 5432:5432 postgres:16
```

Aguarde alguns segundos e conecte pelo DBeaver com os dados abaixo:

- **Host:** `localhost`
- **Porta:** `5432`
- **Usuário:** `postgres`
- **Senha:** `etech123`
- **Banco:** `postgres`

Se a conexão funcionar e você conseguir navegar até o banco `postgres` padrão, o container está saudável.

**Não remova o `meu-postgres`** — ele será reaproveitado na Aula 02.

### Slim vs. imagem completa

Liste as imagens baixadas e repare no tamanho de `python:3.12-slim`:

```bash
docker images | grep python
```

Pesquise rapidamente o tamanho da imagem `python:3.12` completa (sem o `-slim`) e responda por escrito: **por que o Dockerfile do backend, que vamos construir na Aula 02, usa a variante `slim` em vez da imagem completa?**

---

## Checklist final do dia

- [ ] WSL2 confirmado
- [ ] Docker Engine instalado e funcionando (sem Docker Desktop)
- [ ] uv instalado
- [ ] Git configurado
- [ ] DBeaver instalado
- [ ] Repositório do curso clonado
- [ ] Imagens do curso baixadas com `pull_images.sh`
- [ ] Container Nginx testado
- [ ] Container PostgreSQL testado e conectado via DBeaver
- [ ] Resposta sobre `slim` vs imagem completa entregue

---

## Material de apoio

- Docker — instalação no Ubuntu: https://docs.docker.com/engine/install/ubuntu/
- Docker — comandos essenciais: https://docs.docker.com/reference/cli/docker/
- WSL2 — documentação oficial da Microsoft: https://learn.microsoft.com/pt-br/windows/wsl/
- uv — documentação oficial: https://docs.astral.sh/uv/
- DBeaver — documentação oficial: https://dbeaver.io/docs/
- Repositório do curso: https://github.com/douglasdss1995/MCI-05-provisionamento-de-aplicacoes