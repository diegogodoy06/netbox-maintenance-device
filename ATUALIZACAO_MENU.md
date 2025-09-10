# 🎨 Atualização do Menu Lateral - NetBox Maintenance Device

## 📋 **Mudanças Implementadas**

### 🏷️ **1. Nome do Plugin Atualizado**
- **Antes:** "Device Maintenance" / "Plugin"
- **Depois:** "Manutenção de Dispositivos"
- **Arquivo:** `netbox_maintenance_device/__init__.py`

### 🎯 **2. Ícone Principal do Plugin**
- **Ícone:** `mdi-wrench-cog` (chave inglesa com engrenagem)
- **Significado:** Representa manutenção e configuração de dispositivos
- **Localização:** Menu lateral principal do NetBox

### 🔧 **3. Ícones dos Itens do Menu**

| Item do Menu | Ícone | Significado |
|--------------|-------|-------------|
| **Manutenção Próxima** | `mdi-clock-alert-outline` | Relógio com alerta - urgência temporal |
| **Planos de Manutenção** | `mdi-calendar-check` | Calendário marcado - planejamento |
| **Execuções de Manutenção** | `mdi-wrench` | Chave inglesa - execução prática |

### 🌐 **4. Tradução Atualizada**
- Adicionada tradução para "Device Maintenance" → "Manutenção de Dispositivos"
- Tradução compilada e disponível em português brasileiro

## 📁 **Arquivos Modificados**

```
netbox_maintenance_device/
├── __init__.py                     # Nome e ícone do plugin
├── navigation.py                   # Ícones dos itens do menu
└── locale/pt_BR/LC_MESSAGES/
    ├── django.po                   # Tradução atualizada
    └── django.mo                   # Tradução compilada
```

## 🚀 **Como Aplicar as Mudanças**

### 1. **Reinstalar o Plugin**
```bash
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
```

### 2. **Reiniciar o NetBox**
```bash
docker-compose restart netbox
```

### 3. **Verificar no Menu**
- Acesse o NetBox
- Verifique o menu lateral esquerdo
- O plugin agora deve aparecer como "Manutenção de Dispositivos" com ícone de chave inglesa

## 🎨 **Ícones Utilizados**

### **Plugin Principal**
- `mdi-wrench-cog` - Combina manutenção (wrench) com configuração (cog)

### **Itens do Menu**
- `mdi-clock-alert-outline` - Urgência temporal para manutenções próximas
- `mdi-calendar-check` - Planejamento para planos de manutenção
- `mdi-wrench` - Execução prática para execuções de manutenção

## ✅ **Resultado Final**

O menu lateral do NetBox agora apresenta:
- **Nome em português:** "Manutenção de Dispositivos"
- **Ícone intuitivo:** Chave inglesa com engrenagem
- **Submenu organizado:** Cada item com ícone apropriado
- **Tradução completa:** Interface totalmente em português brasileiro

## 📝 **Observações**

- Os ícones utilizam a biblioteca Material Design Icons (MDI)
- Todos os ícones são vetoriais e se adaptam ao tema claro/escuro
- As traduções são carregadas automaticamente baseadas no idioma do usuário
- O design mantém consistência visual com o NetBox

---
**Data:** 10 de setembro de 2025  
**Versão:** 1.1.0  
**Status:** ✅ Implementado
