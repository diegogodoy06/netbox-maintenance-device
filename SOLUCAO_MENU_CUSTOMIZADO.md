# 🔧 Solução: Menu Customizado - NetBox Maintenance Device

## ❌ **Problema Identificado**

O plugin continuava aparecendo como "Plugins" no menu lateral porque estava usando o menu padrão compartilhado do NetBox ao invés de criar seu próprio menu customizado.

### **Causa:**
- Uso de `menu_items` (menu padrão) ao invés de `menu` (menu customizado)
- Menu padrão sempre aparece como "Plugins" independente do `verbose_name`

## ✅ **Solução Implementada**

### **1. Menu Customizado**
Alterado de `menu_items` para `menu` customizado usando `PluginMenu`:

**Antes:**
```python
menu_items = (
    PluginMenuItem(...),
    PluginMenuItem(...),
)
```

**Depois:**
```python
menu = PluginMenu(
    label=_('Manutenção de Dispositivos'),
    groups=(
        (_('Manutenção'), (
            PluginMenuItem(...),
            PluginMenuItem(...),
        )),
    ),
    icon_class='mdi mdi-wrench-cog'
)
```

### **2. Estrutura do Menu Customizado**

| Elemento | Configuração |
|----------|--------------|
| **Label Principal** | "Manutenção de Dispositivos" |
| **Ícone Principal** | `mdi-wrench-cog` (chave inglesa com engrenagem) |
| **Grupo** | "Manutenção" |
| **Itens** | Manutenção Próxima, Planos, Execuções |

### **3. Vantagens do Menu Customizado**

✅ **Nome personalizado:** "Manutenção de Dispositivos" ao invés de "Plugins"  
✅ **Ícone customizado:** Chave inglesa com engrenagem  
✅ **Organização:** Agrupamento lógico dos itens  
✅ **Independência:** Não fica misturado com outros plugins  

## 📁 **Arquivos Modificados**

```
netbox_maintenance_device/
├── navigation.py                   # Menu customizado implementado
├── __init__.py                     # PluginConfig com ícone
└── locale/pt_BR/LC_MESSAGES/
    ├── django.po                   # Traduções atualizadas
    └── django.mo                   # Traduções compiladas
```

## 🌐 **Traduções Adicionadas**

| Texto Original | Tradução |
|----------------|----------|
| `Manutenção de Dispositivos` | `Manutenção de Dispositivos` |
| `Manutenção` | `Manutenção` |
| `Device Maintenance` | `Manutenção de Dispositivos` |

## 🚀 **Como Aplicar as Mudanças**

### **1. Reinstalar o Plugin**
```bash
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
```

### **2. Reiniciar o NetBox**
```bash
docker-compose restart netbox
```

### **3. Verificar o Resultado**
- Acesse o NetBox
- Procure por "Manutenção de Dispositivos" no menu lateral
- O plugin agora deve ter seu próprio menu com ícone

## 📚 **Documentação NetBox**

Baseado na documentação oficial do NetBox:

### **Menu Padrão vs Menu Customizado**

| Tipo | Quando Usar | Resultado |
|------|-------------|-----------|
| `menu_items` | Poucos itens, plugin simples | Aparece em "Plugins" |
| `menu` | Plugin complexo, identidade própria | Menu próprio com nome customizado |

### **Estrutura do PluginMenu**
```python
menu = PluginMenu(
    label='Nome do Menu',           # Aparece no menu lateral
    groups=(                        # Agrupamento dos itens
        ('Grupo 1', (item1, item2)),
        ('Grupo 2', (item3, item4)),
    ),
    icon_class='mdi mdi-icon'       # Ícone do menu
)
```

## ✅ **Resultado Final**

O menu lateral do NetBox agora apresenta:

🔧 **Manutenção de Dispositivos** *(com ícone de chave inglesa)*
- └── **Manutenção**
  - ├── Manutenção Próxima
  - ├── Planos de Manutenção [+]
  - └── Execuções de Manutenção [+]

## 📝 **Observações Técnicas**

1. **PluginMenu vs menu_items:** Menu customizado permite controle total sobre aparência
2. **Compatibilidade:** Funciona em NetBox 4.4 sem problemas
3. **Traduções:** Suporte completo ao português brasileiro
4. **Ícones:** Material Design Icons para consistência visual

---
**Data:** 10 de setembro de 2025  
**Versão:** 1.1.0  
**Status:** ✅ Implementado e Testado  
**Documentação:** [NetBox Plugin Navigation](https://docs.netbox.dev/en/stable/plugins/development/navigation/)
