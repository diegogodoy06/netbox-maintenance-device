# PowerShell Script para Publicação no PyPI
# Uso: .\publish.ps1 [-test] [-version "1.2.2"]

param(
    [switch]$test,
    [string]$version = ""
)

Write-Host "🚀 NetBox Maintenance Device - Publicação PyPI" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray

# Verificar se estamos no diretório correto
if (-not (Test-Path "setup.py")) {
    Write-Host "❌ Erro: setup.py não encontrado. Execute este script no diretório do projeto." -ForegroundColor Red
    exit 1
}

# Verificar dependências
$required_tools = @("python", "git")
foreach ($tool in $required_tools) {
    try {
        & $tool --version | Out-Null
        Write-Host "✅ $tool encontrado" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $tool não encontrado. Instale $tool primeiro." -ForegroundColor Red
        exit 1
    }
}

# Atualizar versão se fornecida
if ($version) {
    Write-Host "📝 Atualizando versão para $version..." -ForegroundColor Yellow
    python bump_version.py $version
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao atualizar versão" -ForegroundColor Red
        exit 1
    }
}

# Verificar se há mudanças não commitadas
$git_status = git status --porcelain
if ($git_status) {
    Write-Host "⚠️  Existem mudanças não commitadas:" -ForegroundColor Yellow
    git status --short
    $confirm = Read-Host "Continuar mesmo assim? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ Publicação cancelada" -ForegroundColor Red
        exit 1
    }
}

# Limpeza
Write-Host "🧹 Limpando builds anteriores..." -ForegroundColor Yellow
Remove-Item -Path "build", "dist", "*.egg-info" -Recurse -Force -ErrorAction SilentlyContinue

# Instalar dependências de build
Write-Host "📦 Instalando dependências de build..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel twine build

# Build
Write-Host "🏗️  Construindo pacote..." -ForegroundColor Yellow
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro durante o build" -ForegroundColor Red
    exit 1
}

# Verificar pacote
Write-Host "✅ Verificando pacote..." -ForegroundColor Yellow
python -m twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro na verificação do pacote" -ForegroundColor Red
    exit 1
}

# Mostrar arquivos criados
Write-Host "📂 Arquivos criados:" -ForegroundColor Blue
Get-ChildItem -Path "dist" | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Cyan }

# Confirmar publicação
if ($test) {
    $target = "TestPyPI"
    $repository_arg = "--repository testpypi"
    $install_url = "https://test.pypi.org/project/netbox-maintenance-device/"
} else {
    $target = "PyPI"
    $repository_arg = ""
    $install_url = "https://pypi.org/project/netbox-maintenance-device/"
}

Write-Host ""
Write-Host "🎯 Destino: $target" -ForegroundColor Magenta
$confirm = Read-Host "Confirma a publicação? (y/N)"

if ($confirm -eq "y" -or $confirm -eq "Y") {
    Write-Host "📤 Publicando no $target..." -ForegroundColor Green
    
    if ($test) {
        python -m twine upload --repository testpypi dist/*
    } else {
        python -m twine upload dist/*
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Publicação realizada com sucesso!" -ForegroundColor Green
        Write-Host "📍 Disponível em: $install_url" -ForegroundColor Cyan
        Write-Host ""
        
        if ($test) {
            Write-Host "🧪 Para testar a instalação:" -ForegroundColor Yellow
            Write-Host "pip install --index-url https://test.pypi.org/simple/ netbox-maintenance-device" -ForegroundColor Gray
        } else {
            Write-Host "📥 Para instalar:" -ForegroundColor Yellow
            Write-Host "pip install netbox-maintenance-device" -ForegroundColor Gray
        }
        
        # Sugerir próximos passos
        if (-not $test) {
            Write-Host ""
            Write-Host "📋 Próximos passos recomendados:" -ForegroundColor Blue
            Write-Host "1. Criar release no GitHub com a tag v$((python -c 'import setup; print(setup.version)' 2>$null) -replace '[^\d\.]','')" -ForegroundColor Gray
            Write-Host "2. Atualizar documentação se necessário" -ForegroundColor Gray
            Write-Host "3. Comunicar a nova versão para a comunidade" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Erro durante a publicação" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Publicação cancelada pelo usuário" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ Script finalizado!" -ForegroundColor Green