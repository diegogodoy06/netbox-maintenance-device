# Sistema de Notificações de Manutenção

## Visão Geral

O NetBox Maintenance Device Plugin inclui um sistema abrangente de notificações que mantém os usuários informados sobre o status das manutenções de dispositivos. O sistema oferece tanto notificações internas do NetBox quanto notificações push do navegador para Windows.

## Funcionalidades

### 1. Tipos de Notificação

- **Overdue (Atrasada)**: Manutenção que deveria ter sido executada
- **Due Soon (Vencendo)**: Manutenção que vence em breve (configurável)
- **Scheduled (Agendada)**: Manutenção foi agendada
- **Completed (Concluída)**: Manutenção foi concluída
- **Cancelled (Cancelada)**: Manutenção foi cancelada

### 2. Níveis de Prioridade

- **Critical**: Para manutenções atrasadas
- **High**: Para manutenções vencendo em 3 dias ou menos
- **Medium**: Para manutenções vencendo em 4-7 dias
- **Low**: Para notificações de conclusão

### 3. Notificações no Navegador

O sistema solicita permissão para enviar notificações do navegador e exibe alertas do Windows quando:
- Novas notificações são criadas
- Manutenções estão atrasadas (prioridade crítica)
- Manutenções vencem em breve

## Configuração

### 1. Instalação Básica

O sistema de notificações é automaticamente configurado quando o plugin é instalado. Nenhuma configuração adicional é necessária.

### 2. Comando de Verificação Manual

Para executar a verificação de notificações manualmente:

```bash
python manage.py check_maintenance_notifications
```

Opções disponíveis:
- `--days-ahead 7`: Quantos dias à frente verificar (padrão: 7)
- `--dry-run`: Simular execução sem criar notificações

### 3. Automação com Celery (Recomendado)

Para automação completa, configure as seguintes tarefas Celery:

```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-maintenance-notifications': {
        'task': 'netbox_maintenance_device.tasks.check_maintenance_notifications',
        'schedule': crontab(hour=8, minute=0),  # Diariamente às 8:00
        'kwargs': {'days_ahead': 7}
    },
    'send-browser-notifications': {
        'task': 'netbox_maintenance_device.tasks.send_browser_notifications',
        'schedule': 300.0,  # A cada 5 minutos
    },
}
```

### 4. Configuração de Permissões

O sistema solicita automaticamente permissão para notificações do navegador. Para configurar manualmente:

1. Acesse as configurações do navegador
2. Vá para Privacidade e Segurança → Notificações
3. Adicione o domínio do NetBox como permitido

## Interface do Usuário

### 1. Indicador de Notificações

Um indicador de sino aparece no cabeçalho do NetBox com:
- Contador de notificações não lidas
- Dropdown com as 5 notificações mais recentes
- Link para visualizar todas as notificações

### 2. Página de Notificações

A página `/plugins/netbox-maintenance-device/notifications/` mostra:
- Lista completa de notificações
- Filtros por tipo e prioridade
- Opções para marcar como lidas
- Status de entrega das notificações do navegador

### 3. Integração com Dispositivos

As notificações aparecem também:
- Na aba de manutenção dos dispositivos
- Na página de planos de manutenção
- No dashboard de manutenções próximas

## API de Notificações

### Endpoints Disponíveis

```
GET /plugins/netbox-maintenance-device/api/notifications/unread/
POST /plugins/netbox-maintenance-device/api/notifications/mark-read/
POST /plugins/netbox-maintenance-device/api/notifications/mark-all-read/
POST /plugins/netbox-maintenance-device/api/notifications/send-browser/
```

### Exemplo de Uso da API

```javascript
// Buscar notificações não lidas
fetch('/plugins/netbox-maintenance-device/api/notifications/unread/')
    .then(response => response.json())
    .then(data => {
        console.log(`${data.count} notificações não lidas`);
    });

// Marcar notificação como lida
fetch('/plugins/netbox-maintenance-device/api/notifications/mark-read/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({notification_id: 123})
});
```

## Personalização

### 1. Usuários para Notificação

Por padrão, o sistema notifica usuários com `is_staff=True`. Para personalizar:

```python
# Em models.py, método create_notification
def get_users_to_notify(self, plan):
    # Personalizar lógica aqui
    # Exemplo: usuários de um grupo específico
    return User.objects.filter(
        groups__name='Maintenance Team',
        is_active=True
    )
```

### 2. Frequência de Verificação

Ajuste a frequência no comando de gerenciamento:

```python
# Para verificar manutenções vencendo em 14 dias
python manage.py check_maintenance_notifications --days-ahead 14
```

### 3. Limpeza de Notificações

Notificações lidas são automaticamente removidas após 30 dias. Para alterar:

```python
# Em tasks.py
old_notifications = MaintenanceNotification.objects.filter(
    is_read=True,
    created_at__lt=timezone.now() - timedelta(days=60)  # 60 dias em vez de 30
)
```

## Monitoramento e Logs

### 1. Logs do Sistema

O sistema registra logs em:
- Criação de notificações
- Erros de processamento
- Limpeza de notificações antigas

```python
import logging
logger = logging.getLogger('netbox_maintenance_device')
```

### 2. Métricas

Monitore as seguintes métricas:
- Número de notificações criadas por dia
- Taxa de leitura de notificações
- Tempo de resposta das APIs
- Erros de permissão do navegador

## Troubleshooting

### 1. Notificações do Navegador Não Funcionam

**Problema**: Notificações não aparecem no Windows
**Soluções**:
1. Verificar se o navegador tem permissão
2. Verificar se as notificações do Windows estão habilitadas
3. Testar em modo privado/incógnito

### 2. Notificações Duplicadas

**Problema**: Múltiplas notificações para a mesma manutenção
**Solução**: O sistema verifica duplicatas por data. Verifique se o comando não está sendo executado múltiplas vezes no mesmo dia.

### 3. Performance

**Problema**: Muitas notificações afetam performance
**Soluções**:
1. Configurar limpeza automática mais frequente
2. Limitar número de notificações por usuário
3. Usar índices de banco de dados apropriados

## Migração e Backup

### 1. Migração do Banco de Dados

```bash
python manage.py migrate netbox_maintenance_device
```

### 2. Backup de Notificações

```sql
-- Backup das notificações
SELECT * FROM netbox_maintenance_device_maintenancenotification 
WHERE created_at >= '2024-01-01';
```

## Integração com Sistemas Externos

### 1. Webhooks

Para integrar com sistemas externos, use sinais Django:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=MaintenanceNotification)
def notify_external_system(sender, instance, created, **kwargs):
    if created and instance.priority == 'critical':
        # Enviar para sistema externo
        pass
```

### 2. APIs REST

Use a API REST do NetBox para integração:

```python
import requests

# Buscar notificações via API
response = requests.get(
    'http://netbox/api/plugins/netbox-maintenance-device/notifications/',
    headers={'Authorization': 'Token your-token'}
)
```
