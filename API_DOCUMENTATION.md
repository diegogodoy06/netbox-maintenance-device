# NetBox Maintenance Device - API Documentation

## Overview

O plugin NetBox Maintenance Device oferece uma API REST completa que permite integração externa com sistemas de monitoramento, automação e gestão de manutenção. A API segue os padrões do NetBox e oferece operações CRUD completas, filtros avançados e ações customizadas.

## Base URL

A API está disponível no endpoint base:
```
https://your-netbox-instance/api/plugins/netbox-maintenance-device/
```

## Authentication

A API utiliza o sistema de autenticação do NetBox, suportando:

- **Token Authentication**: Use o header `Authorization: Token your-api-token`
- **Session Authentication**: Para uso no navegador com login ativo

### Obtendo Token de API

1. Acesse a interface do NetBox
2. Vá em **User Menu > API Tokens**
3. Clique em **Add Token**
4. Configure as permissões necessárias
5. Copie o token gerado

## Permissions

As seguintes permissões são necessárias:

| Operação | Permissão Necessária |
|----------|---------------------|
| **View** | `netbox_maintenance_device.view_maintenanceplan` |
| **Add** | `netbox_maintenance_device.add_maintenanceplan` |
| **Change** | `netbox_maintenance_device.change_maintenanceplan` |
| **Delete** | `netbox_maintenance_device.delete_maintenanceplan` |

## Endpoints

### MaintenancePlan API

#### Base Endpoint: `/maintenance-plans/`

##### List Plans
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/
```

**Query Parameters:**
- `device_id`: Filter by device ID
- `device`: Filter by device name (partial match)
- `maintenance_type`: Filter by type (`preventive`, `corrective`)
- `is_active`: Filter by active status (`true`, `false`)
- `frequency_days`: Filter by exact frequency
- `frequency_days__gte`: Minimum frequency in days
- `frequency_days__lte`: Maximum frequency in days
- `q`: Full-text search across name, description, device
- `ordering`: Sort results (`name`, `device__name`, `frequency_days`, etc.)
- `limit`: Results per page (default: 50)
- `offset`: Pagination offset

**Response Example:**
```json
{
  "count": 25,
  "next": "http://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": 1,
      "url": "http://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/1/",
      "display": "Switch-Core-01 - Monthly Check",
      "device": {
        "id": 123,
        "name": "Switch-Core-01",
        "display": "Switch-Core-01"
      },
      "name": "Monthly Check",
      "description": "Monthly preventive maintenance check",
      "maintenance_type": "preventive",
      "frequency_days": 30,
      "is_active": true,
      "created": "2025-09-17T10:00:00Z",
      "last_updated": "2025-09-17T10:00:00Z",
      "execution_count": 5,
      "next_maintenance_date": "2025-10-17T10:00:00Z",
      "is_overdue": false,
      "days_until_due": 30,
      "last_execution_date": "2025-09-17T09:00:00Z",
      "executions": [
        {
          "id": 10,
          "display": "Switch-Core-01 - Monthly Check - 2025-10-17",
          "scheduled_date": "2025-10-17T09:00:00Z",
          "status": "scheduled"
        }
      ],
      "custom_field_data": {},
      "tags": []
    }
  ]
}
```

##### Create Plan
```http
POST /api/plugins/netbox-maintenance-device/maintenance-plans/
Content-Type: application/json
Authorization: Token your-api-token

{
  "device": 123,
  "name": "Weekly Backup Check",
  "description": "Weekly verification of backup systems",
  "maintenance_type": "preventive",
  "frequency_days": 7,
  "is_active": true
}
```

##### Get Specific Plan
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/1/
```

##### Update Plan
```http
PATCH /api/plugins/netbox-maintenance-device/maintenance-plans/1/
Content-Type: application/json
Authorization: Token your-api-token

{
  "frequency_days": 14,
  "description": "Updated to bi-weekly schedule"
}
```

##### Delete Plan
```http
DELETE /api/plugins/netbox-maintenance-device/maintenance-plans/1/
Authorization: Token your-api-token
```

#### Custom Actions

##### Schedule Maintenance
```http
POST /api/plugins/netbox-maintenance-device/maintenance-plans/1/schedule-maintenance/
Content-Type: application/json
Authorization: Token your-api-token

{
  "scheduled_date": "2025-10-17T09:00:00Z",
  "notes": "Routine monthly maintenance",
  "technician": "John Doe"
}
```

##### Get Overdue Plans
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/overdue/
```

##### Get Upcoming Plans
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/upcoming/?days=30
```

##### Get Statistics
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/statistics/
```

**Response:**
```json
{
  "total_plans": 25,
  "active_plans": 20,
  "inactive_plans": 5,
  "preventive_plans": 18,
  "corrective_plans": 7,
  "overdue_plans": 3
}
```

### MaintenanceExecution API

#### Base Endpoint: `/maintenance-executions/`

##### List Executions
```http
GET /api/plugins/netbox-maintenance-device/maintenance-executions/
```

**Query Parameters:**
- `maintenance_plan_id`: Filter by plan ID
- `maintenance_plan`: Filter by plan name (partial match)
- `device_id`: Filter by device ID
- `device`: Filter by device name (partial match)
- `status`: Filter by status (`scheduled`, `in_progress`, `completed`, `cancelled`)
- `completed`: Filter by completion status (`true`, `false`)
- `scheduled_date`: Filter by exact scheduled date
- `scheduled_date__gte`: Scheduled after date
- `scheduled_date__lte`: Scheduled before date
- `completed_date__gte`: Completed after date
- `completed_date__lte`: Completed before date
- `technician`: Filter by technician name (partial match)
- `q`: Full-text search across plan, device, notes, technician

##### Create Execution
```http
POST /api/plugins/netbox-maintenance-device/maintenance-executions/
Content-Type: application/json
Authorization: Token your-api-token

{
  "maintenance_plan": 1,
  "scheduled_date": "2025-10-17T09:00:00Z",
  "status": "scheduled",
  "notes": "Routine maintenance execution",
  "technician": "Jane Smith"
}
```

#### Custom Actions

##### Complete Execution
```http
POST /api/plugins/netbox-maintenance-device/maintenance-executions/10/complete/
Content-Type: application/json
Authorization: Token your-api-token

{
  "notes": "Maintenance completed successfully. All systems operational.",
  "technician": "Jane Smith"
}
```

##### Cancel Execution
```http
POST /api/plugins/netbox-maintenance-device/maintenance-executions/10/cancel/
Content-Type: application/json
Authorization: Token your-api-token

{
  "notes": "Cancelled due to equipment unavailability"
}
```

##### Get Pending Executions
```http
GET /api/plugins/netbox-maintenance-device/maintenance-executions/pending/
```

##### Get Overdue Executions
```http
GET /api/plugins/netbox-maintenance-device/maintenance-executions/overdue-executions/
```

##### Get Execution Statistics
```http
GET /api/plugins/netbox-maintenance-device/maintenance-executions/statistics/
```

## Error Handling

A API retorna códigos de status HTTP padrão:

- `200 OK`: Sucesso
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Token de autenticação necessário
- `403 Forbidden`: Permissões insuficientes
- `404 Not Found`: Recurso não encontrado
- `405 Method Not Allowed`: Método não permitido
- `500 Internal Server Error`: Erro interno do servidor

**Exemplo de erro:**
```json
{
  "error": "Validation failed",
  "details": {
    "frequency_days": ["Frequency must be greater than 0 days"],
    "name": ["A maintenance plan with name 'Daily Check' already exists for this device."]
  }
}
```

## Rate Limiting

A API segue os limites de rate do NetBox. Por padrão:
- **Authenticated users**: 1000 requests/hour
- **Anonymous users**: 100 requests/hour

## Pagination

Todas as listagens suportam paginação:

```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/?limit=20&offset=40
```

**Response:**
```json
{
  "count": 150,
  "next": "http://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/?limit=20&offset=60",
  "previous": "http://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/?limit=20&offset=20",
  "results": [...]
}
```

## Filtering Examples

### Complex Filtering
```http
GET /api/plugins/netbox-maintenance-device/maintenance-plans/?device=core&maintenance_type=preventive&frequency_days__lte=30&is_active=true&ordering=next_maintenance_date
```

### Search with Filters
```http
GET /api/plugins/netbox-maintenance-device/maintenance-executions/?q=backup&status=completed&completed_date__gte=2025-09-01&ordering=-completed_date
```

## Bulk Operations

### Bulk Creation
```http
POST /api/plugins/netbox-maintenance-device/maintenance-plans/
Content-Type: application/json
Authorization: Token your-api-token

[
  {
    "device": 123,
    "name": "Weekly Check",
    "maintenance_type": "preventive",
    "frequency_days": 7
  },
  {
    "device": 124,
    "name": "Monthly Check",
    "maintenance_type": "preventive", 
    "frequency_days": 30
  }
]
```

## Integration Examples

### Python with requests
```python
import requests

# Setup
base_url = "https://netbox.example.com/api/plugins/netbox-maintenance-device"
headers = {"Authorization": "Token your-api-token"}

# Get all overdue plans
response = requests.get(f"{base_url}/maintenance-plans/overdue/", headers=headers)
overdue_plans = response.json()

# Schedule maintenance for each overdue plan
for plan in overdue_plans['results']:
    schedule_data = {
        "scheduled_date": "2025-10-20T09:00:00Z",
        "technician": "Automated System",
        "notes": "Auto-scheduled overdue maintenance"
    }
    
    requests.post(
        f"{base_url}/maintenance-plans/{plan['id']}/schedule-maintenance/",
        json=schedule_data,
        headers=headers
    )
```

### PowerShell
```powershell
$baseUrl = "https://netbox.example.com/api/plugins/netbox-maintenance-device"
$headers = @{"Authorization" = "Token your-api-token"}

# Get upcoming maintenance in next 7 days
$response = Invoke-RestMethod -Uri "$baseUrl/maintenance-plans/upcoming/?days=7" -Headers $headers
$upcomingPlans = $response.results

# Send notification for each upcoming maintenance
foreach ($plan in $upcomingPlans) {
    Write-Host "Upcoming maintenance for $($plan.device.name): $($plan.name)"
    # Send notification logic here
}
```

### curl
```bash
# Get all active plans
curl -H "Authorization: Token your-api-token" \
     "https://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/?is_active=true"

# Create new plan
curl -X POST \
     -H "Authorization: Token your-api-token" \
     -H "Content-Type: application/json" \
     -d '{"device": 123, "name": "New Plan", "maintenance_type": "preventive", "frequency_days": 30}' \
     "https://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-plans/"

# Complete execution
curl -X POST \
     -H "Authorization: Token your-api-token" \
     -H "Content-Type: application/json" \
     -d '{"notes": "Completed successfully"}' \
     "https://netbox.example.com/api/plugins/netbox-maintenance-device/maintenance-executions/10/complete/"
```

## Webhook Integration

O plugin é compatível com o sistema de webhooks do NetBox. Configure webhooks para receber notificações sobre:

- Criação/atualização de planos de manutenção
- Agendamento de manutenções
- Conclusão de manutenções
- Planos em atraso

**Exemplo de payload do webhook:**
```json
{
  "event": "created",
  "model": "netbox_maintenance_device.maintenanceplan",
  "timestamp": "2025-09-17T10:00:00Z",
  "data": {
    "id": 1,
    "name": "Monthly Check",
    "device": {"id": 123, "name": "Switch-Core-01"},
    "maintenance_type": "preventive",
    "frequency_days": 30
  }
}
```