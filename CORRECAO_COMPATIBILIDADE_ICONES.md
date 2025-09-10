# 🔧 Correção de Compatibilidade - NetBox 4.4

## ❌ **Erro Encontrado**

```
TypeError: PluginMenuItem.__init__() got an unexpected keyword argument 'icon_class'
```

## 🔍 **Diagnóstico**

O NetBox 4.4 não suporta o parâmetro `icon_class` no construtor `PluginMenuItem`. Este parâmetro foi removido ou nunca existiu na versão atual.

## ✅ **Correção Aplicada**

### **Antes (Com Erro):**
```python
PluginMenuItem(
    link='plugins:netbox_maintenance_device:upcoming_maintenance',
    link_text=_('Upcoming Maintenance'),
    permissions=['netbox_maintenance_device.view_maintenanceplan'],
    icon_class='mdi-clock-alert-outline'  # ❌ Não suportado
)
```

### **Depois (Corrigido):**
```python
PluginMenuItem(
    link='plugins:netbox_maintenance_device:upcoming_maintenance',
    link_text=_('Upcoming Maintenance'),
    permissions=['netbox_maintenance_device.view_maintenanceplan']
    # ✅ Sem icon_class nos itens do menu
)
```

## 🎯 **Solução Implementada**

1. **Mantido:** Ícone principal do plugin (`mdi-wrench-cog`) no `__init__.py`
2. **Removido:** Ícones individuais dos itens do menu no `navigation.py`
3. **Preservado:** Ícones dos botões (que continuam funcionando)

## 📁 **Arquivos Modificados**

- `netbox_maintenance_device/navigation.py` - Removidos parâmetros `icon_class` incompatíveis

## 🚀 **Status Final**

- ✅ **Nome do plugin:** "Manutenção de Dispositivos"
- ✅ **Ícone principal:** `mdi-wrench-cog` (funciona)
- ✅ **Menu compatível:** Sem ícones individuais (compatível com NetBox 4.4)
- ✅ **Botões:** Mantêm ícones (funcionam normalmente)

## 📝 **Observações de Compatibilidade**

### **NetBox 4.4 Suporta:**
- ✅ `icon` no `PluginConfig` (ícone principal)
- ✅ `icon_class` no `PluginMenuButton` (botões)
- ❌ `icon_class` no `PluginMenuItem` (itens do menu)

### **Resultado Visual:**
- O plugin aparece com ícone de chave inglesa no menu principal
- Os itens do submenu aparecem sem ícones individuais
- Os botões "Adicionar" mantêm seus ícones de "+"

---
**Data:** 10 de setembro de 2025  
**NetBox:** 4.4.0  
**Status:** ✅ Corrigido e compatível
