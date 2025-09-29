# 🚀 Guia Rápido de Publicação PyPI

## ✅ Problema Resolvido
O erro das GitHub Actions depreciadas foi corrigido! Atualizamos:

- ✅ `actions/upload-artifact@v3` → `v4`
- ✅ `actions/download-artifact@v3` → `v4` 
- ✅ `actions/setup-python@v4` → `v5`
- ✅ `pypa/gh-action-pypi-publish@release/v1` → `v1.10.3`

## 🎯 Como Publicar no PyPI

### Método 1: Automático via GitHub Release (Recomendado)

```bash
# 1. Crie uma nova tag/release
git tag v1.2.1
git push origin v1.2.1

# 2. Vá no GitHub → Releases → Create a new release
# - Tag: v1.2.1  
# - Title: "v1.2.1 - NetBox 4.4.x Compatibility"
# - Description: Cole do CHANGELOG.md
# - Publish release → GitHub Actions irá publicar automaticamente!
```

### Método 2: Manual via Script PowerShell

```powershell
# Para teste no TestPyPI primeiro
.\publish.ps1 -test

# Para publicação real no PyPI
.\publish.ps1
```

### Método 3: Execução Manual do Workflow

1. Vá em **Actions** → **Publish to PyPI**
2. Clique em **Run workflow**
3. Selecione branch `main`
4. Clique **Run workflow** → Irá publicar no TestPyPI

## 🔧 Comandos de Desenvolvimento

```bash
# Atualizar versão
python bump_version.py 1.2.2

# Build local
python -m build

# Verificar pacote
python -m twine check dist/*

# Publicar manualmente
python -m twine upload dist/*
```

## 📋 Checklist Antes de Publicar

- [ ] ✅ Código testado localmente
- [ ] ✅ CHANGELOG.md atualizado
- [ ] ✅ Versão bumped nos arquivos necessários
- [ ] ✅ Commit e push das mudanças
- [ ] ✅ GitHub Actions passando
- [ ] ✅ README atualizado

## 🎉 Resultado

Após a publicação:
- 📦 **Pacote**: https://pypi.org/project/netbox-maintenance-device/
- 📥 **Instalação**: `pip install netbox-maintenance-device`
- 🐳 **Docker**: `echo "netbox-maintenance-device>=1.2.1" >> plugin_requirements.txt`

## 🛡️ Segurança

O projeto agora inclui:
- 🔒 Verificações de segurança automáticas
- 🧪 Testes em múltiplas versões Python
- ✅ Qualidade de código com linting
- 📦 Build automático e verificação

**Tudo pronto para publicação! 🚀**