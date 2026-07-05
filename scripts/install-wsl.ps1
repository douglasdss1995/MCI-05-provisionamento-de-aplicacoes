# =============================================================================
# install-wsl.ps1
# Instalação do WSL2 com Ubuntu 24.04 LTS no Windows 11
#
# Curso: Provisionamento de Aplicações — FPFTech
# Execute este script no PowerShell como Administrador antes do início da Aula 01.
#
# USO:
#   Clique com o botão direito no PowerShell > "Executar como Administrador"
#   .\install-wsl.ps1
#
# O que este script faz:
#   1. Verifica se está rodando como Administrador
#   2. Verifica a versão do Windows
#   3. Habilita os recursos WSL e Plataforma de Máquina Virtual
#   4. Define WSL 2 como versão padrão
#   5. Instala o Ubuntu 24.04 LTS
#   6. Orienta a execução do setup.sh dentro do Ubuntu
#
# ATENÇÃO: Uma reinicialização pode ser necessária após a etapa 3.
#          Se o script solicitar, reinicie e execute novamente.
# =============================================================================

#Requires -RunAsAdministrator

# Configura a saída do console para suportar caracteres especiais
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Interrompe o script imediatamente se qualquer comando retornar erro
$ErrorActionPreference = "Stop"

# Funções de log com cores
function Log-Info  { param($msg) Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Log-Ok    { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Log-Aviso { param($msg) Write-Host "[AVISO] $msg" -ForegroundColor Yellow }
function Log-Erro  { param($msg) Write-Host "[ERRO]  $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Instalação do WSL2 + Ubuntu 24.04 LTS"                       -ForegroundColor Cyan
Write-Host " Curso: Provisionamento de Aplicações — FPFTech"              -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Passo 1: Verificar versão do Windows
# WSL2 requer Windows 10 Build 19041 ou superior (Windows 11 é suficiente)
# -----------------------------------------------------------------------------
Log-Info "Verificando versão do Windows..."

$buildAtual = [System.Environment]::OSVersion.Version.Build
$buildMinimo = 19041

if ($buildAtual -lt $buildMinimo) {
    Log-Erro "Windows desatualizado. Build atual: $buildAtual. Mínimo exigido: $buildMinimo."
    Log-Erro "Atualize o Windows antes de continuar."
    exit 1
}

Log-Ok "Versão do Windows compatível (Build $buildAtual)."

# -----------------------------------------------------------------------------
# Passo 2: Verificar se o WSL já está instalado e funcional
# Se já estiver, pulamos a instalação para não sobrescrever configurações
# -----------------------------------------------------------------------------
Log-Info "Verificando se o WSL já está instalado..."

$wslInstalado = $false
try {
    $wslStatus = wsl --status 2>&1
    if ($LASTEXITCODE -eq 0) {
        $wslInstalado = $true
    }
} catch {
    $wslInstalado = $false
}

if ($wslInstalado) {
    Log-Aviso "WSL já está instalado neste computador."
    Log-Aviso "Verificando se o Ubuntu 24.04 já está disponível..."

    $distribuicoes = wsl --list --quiet 2>&1
    if ($distribuicoes -match "Ubuntu-24.04") {
        Log-Ok "Ubuntu 24.04 LTS já está instalado. Nada a fazer."
        Write-Host ""
        Write-Host "  Para abrir o Ubuntu, execute no PowerShell:"
        Write-Host "    wsl -d Ubuntu-24.04" -ForegroundColor Yellow
        Write-Host ""
        exit 0
    }

    Log-Info "Ubuntu 24.04 não encontrado. Instalando..."
}

# -----------------------------------------------------------------------------
# Passo 3: Habilitar o recurso Windows Subsystem for Linux
# Este é o componente base do WSL no Windows
# -----------------------------------------------------------------------------
Log-Info "Habilitando recurso: Windows Subsystem for Linux..."

$recursoWSL = Get-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux"
if ($recursoWSL.State -ne "Enabled") {
    Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux" -NoRestart
    Log-Ok "Recurso WSL habilitado."
} else {
    Log-Ok "Recurso WSL já estava habilitado."
}

# -----------------------------------------------------------------------------
# Passo 4: Habilitar o recurso Plataforma de Máquina Virtual
# Obrigatório para o WSL 2 — permite a execução de VMs leves (Hyper-V)
# -----------------------------------------------------------------------------
Log-Info "Habilitando recurso: Plataforma de Maquina Virtual..."

$recursoVM = Get-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform"
if ($recursoVM.State -ne "Enabled") {
    Enable-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform" -NoRestart
    Log-Ok "Plataforma de Maquina Virtual habilitada."
} else {
    Log-Ok "Plataforma de Maquina Virtual ja estava habilitada."
}

# -----------------------------------------------------------------------------
# Passo 5: Atualizar o kernel do WSL2
# O Windows Update nem sempre entrega a versão mais recente do kernel WSL
# O update manual garante compatibilidade com Docker Engine
# -----------------------------------------------------------------------------
Log-Info "Atualizando o kernel do WSL2..."
try {
    wsl --update
    Log-Ok "Kernel do WSL2 atualizado."
} catch {
    Log-Aviso "Nao foi possivel atualizar o kernel automaticamente."
    Log-Aviso "Se tiver problemas, acesse: https://aka.ms/wsl2kernel"
}

# -----------------------------------------------------------------------------
# Passo 6: Definir WSL 2 como versão padrão
# Sem isso, novas distribuições podem ser instaladas no modo WSL 1 (legado)
# -----------------------------------------------------------------------------
Log-Info "Definindo WSL 2 como versao padrao..."
wsl --set-default-version 2
Log-Ok "WSL 2 definido como padrao."

# -----------------------------------------------------------------------------
# Passo 7: Instalar o Ubuntu 24.04 LTS
# O flag --no-launch evita abrir o terminal do Ubuntu imediatamente
# A configuração de usuário será feita na primeira abertura manual
# -----------------------------------------------------------------------------
Log-Info "Instalando Ubuntu 24.04 LTS (isso pode demorar alguns minutos)..."
Log-Aviso "Nao feche esta janela durante o download."

wsl --install -d Ubuntu-24.04 --no-launch

if ($LASTEXITCODE -ne 0) {
    Log-Erro "Falha ao instalar o Ubuntu 24.04."
    Log-Erro "Tente manualmente: wsl --install -d Ubuntu-24.04"
    exit 1
}

Log-Ok "Ubuntu 24.04 LTS instalado com sucesso."

# -----------------------------------------------------------------------------
# Passo 8: Verificar se reinicialização é necessária
# Alguns ambientes precisam reiniciar para ativar os recursos habilitados
# -----------------------------------------------------------------------------
$precisaReiniciar = $false

$estadoWSL = Get-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux"
$estadoVM  = Get-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform"

if ($estadoWSL.RestartNeeded -or $estadoVM.RestartNeeded) {
    $precisaReiniciar = $true
}

# -----------------------------------------------------------------------------
# Conclusão
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Log-Ok "Instalacao concluida!"
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

if ($precisaReiniciar) {
    Log-Aviso "E necessario reiniciar o computador para concluir a configuracao."
    Write-Host ""
    Write-Host "  Apos reiniciar, siga os proximos passos abaixo." -ForegroundColor Yellow
    Write-Host ""

    # Pergunta se o usuário quer reiniciar agora
    $resposta = Read-Host "Deseja reiniciar agora? (s/N)"
    if ($resposta -match "^[sS]$") {
        Log-Info "Reiniciando em 10 segundos... Salve seu trabalho."
        Start-Sleep -Seconds 10
        Restart-Computer -Force
    } else {
        Log-Aviso "Reinicie manualmente antes de continuar."
    }
} else {
    Write-Host "  Proximos passos:"
    Write-Host ""
    Write-Host "  1. Abra o Ubuntu 24.04 pelo Menu Iniciar" -ForegroundColor Yellow
    Write-Host "     ou execute no PowerShell: wsl -d Ubuntu-24.04" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. Na primeira abertura, crie seu usuario e senha do Linux" -ForegroundColor Yellow
    Write-Host "     (escolha um nome de usuario simples, sem espacos)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  3. Dentro do Ubuntu, execute o script de configuracao:" -ForegroundColor Yellow
    Write-Host "     chmod +x setup.sh && ./setup.sh" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  O setup.sh instala o Docker Engine, o uv e valida o ambiente." -ForegroundColor Gray
    Write-Host ""
}
