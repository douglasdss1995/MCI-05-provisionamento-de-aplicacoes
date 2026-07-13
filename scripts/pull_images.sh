#!/bin/bash
# =============================================================================
# pull_images.sh
# Download antecipado de todas as imagens Docker usadas no curso
#
# Curso: Provisionamento de Aplicações — FPFTech
# Execute este script no início do curso para evitar downloads durante as aulas.
# A rede das salas de aula pode ser lenta — fazer o pull antes economiza tempo.
#
# USO:
#   chmod +x pull_images.sh
#   ./pull_images.sh
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
log_erro()  { echo -e "${COR_ERRO}[ERRO]${SEM_COR}  $1"; }

# -----------------------------------------------------------------------------
# Verificação: Docker deve estar acessível antes de continuar
# -----------------------------------------------------------------------------
if ! docker info &>/dev/null; then
    log_erro "Docker não está acessível. Execute: sudo service docker start"
    log_erro "Se acabou de instalar, feche e reabra o terminal primeiro."
    exit 1
fi

# -----------------------------------------------------------------------------
# Lista de imagens do curso
#
# python:3.12-slim   — base do backend Django (imagem enxuta, sem pacotes extras)
# node:20-alpine     — build do frontend Angular (alpine = imagem mínima)
# nginx:alpine       — servidor web / proxy reverso (alpine = imagem mínima)
# postgres:16        — banco de dados relacional do curso
# alpine:latest      — imagem base para scripts e utilitários
# -----------------------------------------------------------------------------
IMAGENS=(
    "python:3.12-slim"
    "node:20-alpine"
    "nginx:alpine"
    "postgres:16"
    "alpine:latest"
)

echo ""
echo "============================================================"
echo " Iniciando download das imagens Docker do curso"
echo " Total: ${#IMAGENS[@]} imagens"
echo "============================================================"
echo ""

# Contadores para o resumo final
SUCESSO=0
FALHA=0
IMAGENS_COM_FALHA=()

# -----------------------------------------------------------------------------
# Loop principal: faz o pull de cada imagem e registra o resultado
# -----------------------------------------------------------------------------
for IMAGEM in "${IMAGENS[@]}"; do
    log_info "Baixando: ${IMAGEM}..."

    if docker pull "$IMAGEM"; then
        log_ok "Concluído: ${IMAGEM}"
        SUCESSO=$((SUCESSO + 1))
    else
        log_erro "Falha ao baixar: ${IMAGEM}"
        FALHA=$((FALHA + 1))
        IMAGENS_COM_FALHA+=("$IMAGEM")
    fi

    echo ""
done

# -----------------------------------------------------------------------------
# Resumo final
# -----------------------------------------------------------------------------
echo "============================================================"
echo " Resumo do download"
echo "============================================================"
log_ok "Imagens baixadas com sucesso: ${SUCESSO}"

if [ "$FALHA" -gt 0 ]; then
    log_erro "Imagens com falha: ${FALHA}"
    for IMG in "${IMAGENS_COM_FALHA[@]}"; do
        echo "  - ${IMG}"
    done
    echo ""
    log_erro "Tente executar o script novamente ou faça o pull manual:"
    for IMG in "${IMAGENS_COM_FALHA[@]}"; do
        echo "  docker pull ${IMG}"
    done
    exit 1
fi

echo ""
echo "  Todas as imagens estão disponíveis localmente."
echo "  Para listar as imagens baixadas:"
echo "    docker images"
echo ""
