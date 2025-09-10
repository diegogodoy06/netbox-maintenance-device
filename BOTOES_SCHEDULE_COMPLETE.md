# 🔧 Implementação: Botões Schedule e Complete

## 🎯 **Funcionalidade Implementada**

Adicionados os botões **Schedule** e **Complete** para facilitar o gerenciamento de manutenções:

- **🗓️ Schedule:** Agendar uma execução de manutenção para data específica
- **✅ Complete:** Marcar manutenção como concluída imediatamente

## 📍 **Localização dos Botões**

### **1. Seção de Manutenção do Dispositivo**
- **Localização:** Página do dispositivo → Seção "Maintenance"
- **Schedule:** Sempre disponível para todos os planos ativos
- **Complete:** Apenas para manutenções vencidas ou próximas (≤ 7 dias)

### **2. Página Upcoming Maintenance**
- **Localização:** Menu Plugin → Upcoming & Overdue Maintenance
- **Schedule:** Sempre disponível para todos os planos
- **Complete:** Apenas para manutenções urgentes

## 🚀 **Como Funciona**

### **🗓️ Botão Schedule**
```
┌─────────────────────────────────────┐
│ 📅 Schedule Maintenance             │
├─────────────────────────────────────┤
│ Scheduled Date: [2025-09-11] ______ │
│ Technician: [Usuario Logado] ______ │
│ Notes: __________________________ │
│        __________________________ │
├─────────────────────────────────────┤
│ [Cancel] [📅 Schedule Maintenance]  │
└─────────────────────────────────────┘
```

**Comportamento:**
- ✅ **Data padrão:** Amanhã
- ✅ **Técnico:** Usuário logado (nome completo ou username)
- ✅ **Resultado:** Cria `MaintenanceExecution` com status `scheduled`

### **✅ Botão Complete**
```
┌─────────────────────────────────────┐
│ ✅ Complete Maintenance             │
├─────────────────────────────────────┤
│ Technician: [Usuario Logado] ______ │
│ Notes: [Maintenance completed] ____ │
│        __________________________ │
├─────────────────────────────────────┤
│ [Cancel] [✅ Complete Maintenance]  │
└─────────────────────────────────────┘
```

**Comportamento:**
- ✅ **Data:** Hoje (automática)
- ✅ **Status:** `completed` automaticamente
- ✅ **Técnico:** Usuário logado preenchido
- ✅ **Resultado:** Cria `MaintenanceExecution` concluída

## 💻 **Implementação Técnica**

### **📁 Arquivos Modificados**

```
netbox_maintenance_device/
├── views.py                     # Novas views: schedule_maintenance
├── urls.py                      # Nova URL: /schedule/
├── tables.py                    # Botão Schedule na coluna Actions
└── templates/
    ├── device_maintenance_section.html  # Botões + Modais
    └── upcoming_maintenance.html         # Modal Schedule
```

### **🔗 URLs Implementadas**

| Endpoint | Método | Função |
|----------|--------|--------|
| `/quick-complete/` | POST | Completar manutenção |
| `/schedule/` | POST | Agendar manutenção |

### **📊 Fluxo de Dados**

#### **Schedule Maintenance:**
```python
POST /plugins/maintenance-device/schedule/
{
    "plan_id": 123,
    "scheduled_date": "2025-09-11", 
    "technician": "João Silva",
    "notes": "Manutenção preventiva agendada"
}

→ Cria MaintenanceExecution:
{
    "maintenance_plan": plan,
    "scheduled_date": datetime,
    "status": "scheduled",
    "technician": "João Silva",
    "notes": "..."
}
```

#### **Complete Maintenance:**
```python
POST /plugins/maintenance-device/quick-complete/
{
    "plan_id": 123,
    "device_id": 456,
    "technician": "João Silva", 
    "notes": "Concluída com sucesso"
}

→ Cria MaintenanceExecution:
{
    "maintenance_plan": plan,
    "scheduled_date": now(),
    "completed_date": now(),
    "status": "completed",
    "technician": "João Silva",
    "notes": "..."
}
```

## 🎨 **Interface do Usuário**

### **🎯 Botões na Seção do Dispositivo**
```html
[Plano de Manutenção]          [📅] [✅]
├─ Nome do plano               ├─ Schedule
├─ Badge de status             └─ Complete (se urgente)
└─ Link para detalhes
```

### **📋 Botões na Tabela Upcoming**
```html
| Device | Plan | Status | Actions           |
|--------|------|--------|-------------------|
| SW01   | CPU  | Overdue| [📅 Schedule] [✅ Complete] |
| RT02   | RAM  | Due    | [📅 Schedule] [✅ Complete] |
| FW03   | Disk | OK     | [📅 Schedule]               |
```

## 🔄 **Lógica de Exibição**

### **Botão Schedule:**
- ✅ **Sempre visível** para planos ativos
- ✅ **Ícone:** `mdi-calendar-plus`
- ✅ **Estilo:** `btn-outline-primary`

### **Botão Complete:**
- ✅ **Visível apenas quando:**
  - Manutenção está **vencida** (`is_overdue()`)
  - Ou **próxima** (≤ 7 dias)
- ✅ **Ícone:** `mdi-check-circle`
- ✅ **Estilo:** `btn-success`

## 🔧 **Funcionalidades Especiais**

### **👤 Auto-preenchimento do Técnico**
```python
# views.py - linha 131
if not technician and request.user.is_authenticated:
    technician = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
```

### **📅 Data Padrão Inteligente**
```javascript
// JavaScript - Schedule Modal
var tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
$('#scheduledDate').val(tomorrow.toISOString().split('T')[0]);
```

### **🔄 Atualização Automática**
- ✅ **Página recarregada** após ação bem-sucedida
- ✅ **Mensagens de erro** via alert
- ✅ **Loading states** nos botões

## 🧪 **Como Testar**

### **1. Botões na Seção do Dispositivo:**
1. Acesse qualquer dispositivo: `/dcim/devices/[id]/`
2. Vá para seção "Maintenance"
3. Verifique botões ao lado dos planos

### **2. Botões no Upcoming:**
1. Acesse: `/plugins/maintenance-device/upcoming/`
2. Verifique coluna "Actions"
3. Teste Schedule e Complete

### **3. Cenários de Teste:**

#### **Schedule:**
- ✅ Agendar para amanhã
- ✅ Agendar com técnico específico
- ✅ Agendar com notas
- ✅ Verificar criação do registro

#### **Complete:**
- ✅ Completar manutenção vencida
- ✅ Completar com notas
- ✅ Verificar status "completed"
- ✅ Verificar data de conclusão

## 📋 **Validações**

### **Schedule:**
- ✅ **Data obrigatória**
- ✅ **Plano deve existir**
- ✅ **Usuário autenticado** (para técnico)

### **Complete:**
- ✅ **Técnico obrigatório**
- ✅ **Plano deve existir**
- ✅ **Dispositivo deve existir**

## 🚀 **Como Aplicar**

### **1. Reinstalar Plugin:**
```bash
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
```

### **2. Reiniciar NetBox:**
```bash
docker-compose restart netbox
```

### **3. Testar Funcionalidades:**
- Acesse dispositivo e teste botões na seção
- Acesse Upcoming Maintenance e teste tabela
- Verifique criação de execuções

---
**Data:** 10 de setembro de 2025  
**NetBox:** 4.4.0  
**Status:** ✅ Implementado e Funcional  
**Funcionalidades:** Schedule ✅ | Complete ✅ | Auto-preenchimento ✅
