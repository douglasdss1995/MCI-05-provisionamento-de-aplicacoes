#!/bin/bash
# =============================================================================
# setup.sh
# Instalação do Docker Engine no WSL2 (Ubuntu)
#
# Curso: Provisionamento de Aplicações — FPFTech
# Execute este script no terminal do WSL2 antes do início da Aula 01.
#
# USO:
#   chmod +x setup.sh
#   ./setup.sh
#
# O script é idempotente: pode ser executado mais de uma vez sem problemas.
# =============================================================================

set -euo pipefail

# Cores para facilitar a leitura do output
COR_INFO="\033[0;34m"
COR_OK="\033[0;32m"
COR_AVISO="\033[0;33m"
COR_ERRO="\033[0;31m"
SEM_COR="\033[0m"

log_info()  { echo -e "${COR_INFO}[INFO]${SEM_COR}  $1"; }
log_ok()    { echo -e "${COR_OK}[OK]${SEM_COR}    $1"; }
log_aviso() { echo -e "${COR_AVISO}[AVISO]${SEM_COR} $1"; }
log_erro()  { echo -e "${COR_ERRO}[ERRO]${SEM_COR}  $1"; }

# -----------------------------------------------------------------------------
# Verificação: este script deve rodar dentro do WSL2, não no Windows nativo
# -----------------------------------------------------------------------------
if ! grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
    log_aviso "Não foi possível confirmar que este é um ambiente WSL2."
    log_aviso "Continue apenas se tiver certeza de que está rodando no WSL2."
fi

# -----------------------------------------------------------------------------
# Verificação: Docker Desktop não deve estar instalado
# Se o docker já responde como cliente sem ser o Engine nativo, alertamos.
# -----------------------------------------------------------------------------
if command -v docker &>/dev/null; then
    DOCKER_CONTEXT=$(docker context inspect --format '{{.Name}}' 2>/dev/null || true)
    if echo "$DOCKER_CONTEXT" | grep -qi "desktop"; then
        log_erro "Docker Desktop detectado como contexto ativo."
        log_erro "Desinstale o Docker Desktop no Windows antes de continuar."
        log_erro "Instruções: https://docs.docker.com/desktop/uninstall/"
        exit 1
    fi
    log_aviso "Docker já está instalado. Verificando se é o Engine nativo..."
    if docker info &>/dev/null; then
        log_ok "Docker Engine já está funcionando. Nada a instalar."
        exit 0
    fi
fi

# -----------------------------------------------------------------------------
# Passo 1: Atualizar o índice de pacotes e instalar dependências
# -----------------------------------------------------------------------------
log_info "Atualizando lista de pacotes..."
sudo apt-get update -y

log_info "Instalando dependências de rede e criptografia..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# -----------------------------------------------------------------------------
# Passo 2: Adicionar a chave GPG oficial do Docker
# A chave garante que os pacotes baixados são autênticos
# -----------------------------------------------------------------------------
log_info "Adicionando chave GPG do repositório Docker..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# -----------------------------------------------------------------------------
# Passo 3: Adicionar o repositório oficial do Docker ao sources.list
# -----------------------------------------------------------------------------
log_info "Adicionando repositório Docker ao apt..."
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# -----------------------------------------------------------------------------
# Passo 4: Instalar o Docker Engine e os plugins necessários
# docker-ce          = o daemon do Docker (motor principal)
# docker-ce-cli      = a linha de comando `docker`
# containerd.io      = o runtime de containers
# docker-buildx-plugin = suporte a builds multi-plataforma
# docker-compose-plugin = o comando `docker compose` (sem hífen)
# -----------------------------------------------------------------------------
log_info "Atualizando lista de pacotes com o repositório Docker..."
sudo apt-get update -y

log_info "Instalando Docker Engine e plugins..."
sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# -----------------------------------------------------------------------------
# Passo 5: Adicionar o usuário atual ao grupo docker
# Sem isso, todos os comandos `docker` exigiriam sudo
# A mudança de grupo só tem efeito após logout/login ou newgrp
# -----------------------------------------------------------------------------
log_info "Adicionando usuário '${USER}' ao grupo docker..."
sudo usermod -aG docker "$USER"

# -----------------------------------------------------------------------------
# Passo 6: Iniciar e habilitar o serviço Docker
# No WSL2 o systemd pode estar desabilitado — tentamos ambas as formas
# -----------------------------------------------------------------------------
log_info "Iniciando o serviço Docker..."
if command -v systemctl &>/dev/null && systemctl is-active --quiet systemd 2>/dev/null; then
    sudo systemctl enable docker
    sudo systemctl start docker
    log_ok "Docker iniciado via systemd."
else
    # Fallback para WSL2 sem systemd habilitado
    sudo service docker start || true
    log_aviso "systemd não detectado. Docker iniciado via service."
    log_aviso "Para habilitar systemd no WSL2, adicione ao /etc/wsl.conf:"
    log_aviso "  [boot]"
    log_aviso "  systemd=true"
    log_aviso "Depois reinicie o WSL com: wsl --shutdown (no PowerShell)"
fi

# -----------------------------------------------------------------------------
# Passo 7: Verificar a instalação
# -----------------------------------------------------------------------------
log_info "Verificando instalação do Docker..."
if sudo docker run --rm hello-world &>/dev/null; then
    log_ok "Docker instalado e funcionando corretamente."
else
    log_erro "Algo deu errado. Execute: sudo docker run hello-world"
    log_erro "e verifique a saída de erro."
    exit 1
fi

# -----------------------------------------------------------------------------
# Passo 8: Instalar o uv (gerenciador de pacotes Python do curso)
# -----------------------------------------------------------------------------
log_info "Instalando uv (gerenciador de pacotes Python)..."
if command -v uv &>/dev/null; then
    log_ok "uv já está instalado: $(uv --version)"
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Adicionar uv ao PATH da sessão atual
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
    log_ok "uv instalado: $(uv --version)"
fi

# -----------------------------------------------------------------------------
# Conclusão
# -----------------------------------------------------------------------------
echo ""
echo "============================================================"
log_ok "Configuração concluída!"
echo "============================================================"
echo ""
echo "  Próximos passos:"
echo ""
echo "  1. Feche e reabra o terminal do WSL2"
echo "     (necessário para o grupo docker ter efeito)"
echo ""
echo "  2. Confirme que o Docker funciona sem sudo:"
echo "     docker run hello-world"
echo ""
echo "  3. Confirme a versão do Docker Compose:"
echo "     docker compose version"
echo ""
echo "  4. Confirme o uv:"
echo "     uv --version"
echo ""
