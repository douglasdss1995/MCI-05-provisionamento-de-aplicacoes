# MCI-05-provisionamento-de-aplicacoes
Repositório para utilização no curso de Provisionamento de Aplicações

### Passo 1 — Verificar se o Docker Desktop está instalado

O curso **não usa** o Docker Desktop. Se ele estiver instalado, você precisa desinstalá-lo antes de continuar.

**Como verificar:**

1. Pressione `Win + R`, digite `appwiz.cpl` e pressione Enter
2. Na lista de programas, procure por **Docker Desktop**
3. Se encontrar, clique com o botão direito > **Desinstalar**
4. Reinicie o computador após a desinstalação

Se o Docker Desktop **não** estiver na lista, pode ir direto para o Passo 2.

---

### Passo 2 — Instalar o WSL2 com Ubuntu 24.04

O WSL2 (Windows Subsystem for Linux) é o que permite rodar o Linux dentro do Windows. Vamos instalar o Ubuntu 24.04 LTS, que é a distribuição usada no curso.

**Como executar o script:**

1. Abra o menu Iniciar e pesquise por **PowerShell**
2. Clique com o botão direito em **Windows PowerShell** e selecione **Executar como Administrador**
3. Uma janela azul vai abrir. Você verá o texto `PS C:\Windows\system32>`
4. Navegue até a pasta dos scripts. Substitua o caminho pelo caminho real no seu computador:

```powershell
cd "C:\caminho\para\Provisionamento de Aplicações\scripts"
```

1. Antes de executar o script, permita que o PowerShell rode scripts locais:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Quando perguntar, pressione `S` e depois `Enter`.

1. Execute o script de instalação:

```powershell
.\install-wsl.ps1
```

1. Aguarde a conclusão. O script vai mostrar mensagens em verde `[OK]` ou amarelo `[AVISO]`.

> **Atenção:** O script pode pedir para reiniciar o computador. Se isso acontecer, salve tudo o que estiver aberto, confirme a reinicialização e, depois de reiniciar, execute o script novamente — ele vai continuar de onde parou.

**O que o script instala:**

| Componente                    | Para que serve                            |
| ----------------------------- | ----------------------------------------- |
| WSL2                          | Camada que permite rodar Linux no Windows |
| Plataforma de Máquina Virtual | Necessário para o WSL2 funcionar          |
| Ubuntu 24.04 LTS              | O sistema operacional Linux do curso      |

---

### Passo 3 — Configurar o Ubuntu pela primeira vez

Após a instalação, você precisa abrir o Ubuntu e criar seu usuário.

1. Abra o menu Iniciar e pesquise por **Ubuntu 24.04**
2. Clique para abrir. Uma janela preta vai aparecer
3. Aguarde a mensagem: `Enter new UNIX username:`
4. Digite um nome de usuário **sem espaços e sem letras maiúsculas** (exemplo: `joao` ou `maria`)
5. Pressione Enter
6. Digite uma senha. **As letras não aparecem na tela enquanto você digita** — isso é normal
7. Digite a senha novamente para confirmar

> **Dica:** Anote sua senha em algum lugar seguro. Você vai precisar dela sempre que o Ubuntu pedir confirmação de um comando.

---

### Passo 4 — Instalar o Docker Engine e o uv

Com o Ubuntu aberto, agora vamos instalar o Docker Engine (motor de containers) e o `uv` (gerenciador de pacotes Python).

1. Dentro do terminal do Ubuntu, navegue até a pasta do curso.

   > O Windows monta suas pastas dentro do Linux no caminho `/mnt/c/`. Por exemplo, se o repositório está em `C:\Users\SeuNome\Documentos\Provisionamento de Aplicações`, o caminho no Linux seria `/mnt/c/Users/SeuNome/Documentos/Provisionamento de Aplicações`.

   ```bash
   cd "/mnt/c/caminho/para/Provisionamento de Aplicações/scripts"
   ```

2. Dê permissão de execução ao script:

   ```bash
   chmod +x setup.sh
   ```

3. Execute o script:

   ```bash
   ./setup.sh
   ```

4. Quando o script pedir sua senha (para comandos com `sudo`), digite a senha que você criou no Passo 3.

5. Aguarde a conclusão. O processo pode demorar alguns minutos dependendo da internet.

**O que o script instala:**

| Componente              | Para que serve                                 |
| ----------------------- | ---------------------------------------------- |
| `docker-ce`             | O motor principal do Docker                    |
| `docker-ce-cli`         | O comando `docker` no terminal                 |
| `containerd.io`         | O runtime que executa os containers            |
| `docker-buildx-plugin`  | Suporte a builds avançados                     |
| `docker-compose-plugin` | O comando `docker compose` (sem hífen)         |
| `uv`                    | Gerenciador de pacotes Python moderno e rápido |

---

### Passo 5 — Confirmar que tudo funciona

Após o script terminar, **feche e reabra o terminal do Ubuntu**. Isso é necessário para que as configurações de grupo do Docker tenham efeito.

Execute os comandos abaixo para confirmar que tudo está instalado:

```bash
# Verificar a versão do Docker
docker --version

# Verificar a versão do Docker Compose
docker compose version

# Rodar o container de teste (confirma que o Docker está funcionando)
docker run hello-world

# Verificar a versão do uv
uv --version
```

Se todos os comandos retornarem uma versão sem erro, seu ambiente está pronto.

---

### Passo 6 — Baixar as imagens Docker do curso

Para evitar problemas de internet durante as aulas, vamos baixar todas as imagens Docker com antecedência.

Ainda no terminal do Ubuntu, execute:

```bash
chmod +x pull_images.sh
./pull_images.sh
```

O script vai baixar as seguintes imagens:

| Imagem             | Para que serve               |
| ------------------ | ---------------------------- |
| `python:3.12-slim` | Base do backend Django       |
| `node:20-alpine`   | Build do frontend Angular    |
| `nginx:alpine`     | Servidor web e proxy reverso |
| `postgres:16`      | Banco de dados relacional    |
| `alpine:latest`    | Imagem base para utilitários |

Após o download, você pode confirmar com:

```bash
docker images
```
