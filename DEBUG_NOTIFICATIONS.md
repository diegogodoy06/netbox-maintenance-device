# Diagnóstico das Notificações - Debug

## 🔍 Verificações para Fazer

### 1. Verificar se o Template do Indicador está Carregando
1. Acesse o NetBox
2. Abra o console do navegador (F12)
3. Procure por erros JavaScript
4. Verifique se há requests para `/api/plugins/netbox-maintenance-device/api/notifications/unread/`

### 2. Verificar se as Notificações Estão no Banco
Execute no shell do NetBox:

```python
from netbox_maintenance_device.models import MaintenanceNotification
from django.contrib.auth import get_user_model

User = get_user_model()

# Verificar seu usuário
user = User.objects.get(username='diego.godoy')
print(f"Usuário: {user.username}")

# Ver todas as notificações do usuário
notifications = MaintenanceNotification.objects.filter(user=user)
print(f"Total de notificações: {notifications.count()}")

for notif in notifications:
    print(f"- {notif.title} | Read: {notif.is_read} | Created: {notif.created_at}")
```

### 3. Testar API Diretamente
No navegador, acesse:
```
https://ntbx.steelbras.com.br/plugins/netbox-maintenance-device/api/notifications/unread/
```

### 4. Verificar se o Template está Incluído
O indicador de notificações precisa ser incluído no template base do NetBox.

## 🛠️ Possíveis Problemas e Soluções

### Problema 1: Template não incluído no base.html
**Solução**: Adicionar o template no base template ou via plugin template extension

### Problema 2: URLs não mapeadas corretamente
**Solução**: Verificar se as URLs estão corretas

### Problema 3: JavaScript não está carregando
**Solução**: Verificar console do navegador

### Problema 4: CSRF Token
**Solução**: Verificar se o CSRF token está sendo passado

## 🎯 Próximos Passos
1. Execute as verificações acima
2. Reporte os resultados
3. Implementaremos a correção necessária
