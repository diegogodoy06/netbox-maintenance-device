# Configuração Completa de Tradução - NetBox Maintenance Device

## Configuração Realizada

### 1. Arquivos de Tradução Criados
- ✅ `netbox_maintenance_device/locale/pt_BR/LC_MESSAGES/django.po` - Arquivo de tradução fonte
- ✅ `netbox_maintenance_device/locale/pt_BR/LC_MESSAGES/django.mo` - Arquivo compilado (55 traduções)

### 2. Modelos Atualizados com Traduções
- ✅ `models.py` - Adicionados verbose_name e verbose_name_plural traduzidos
- ✅ `forms.py` - Import de gettext_lazy adicionado
- ✅ `__init__.py` - Configuração de locale_paths adicionada

### 3. Traduções Incluídas (55 strings)

#### Tipos de Manutenção:
- Preventive → Preventiva
- Corrective → Corretiva

#### Campos dos Modelos:
- Name → Nome
- Description → Descrição
- Maintenance Type → Tipo de Manutenção
- Frequency (days) → Frequência (dias)
- Active → Ativo
- Device → Dispositivo
- Scheduled Date → Data Agendada
- Completed Date → Data de Conclusão
- Status → Status
- Notes → Observações
- Technician → Técnico

#### Status de Execução:
- Scheduled → Agendado
- In Progress → Em Andamento
- Completed → Concluído
- Cancelled → Cancelado

#### Interface do Usuário:
- Add Maintenance Plan → Adicionar Plano de Manutenção
- Add Execution → Adicionar Execução
- View Maintenance → Ver Manutenção
- Maintenance Plans → Planos de Manutenção
- Schedule Immediate Maintenance → Agendar Manutenção Imediata
- Mark as Completed → Marcar como Concluído
- No maintenance plans configured → Nenhum plano de manutenção configurado
- Recent Maintenance History → Histórico Recente de Manutenção

## Para Ativar as Traduções no NetBox

### 1. Configuração no NetBox (configuration.py)

Adicione ou modifique as seguintes configurações no seu arquivo `configuration.py`:

```python
# Configurações de Internacionalização
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurar idioma padrão para Português Brasileiro
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

# Idiomas disponíveis
LANGUAGES = [
    ('en', 'English'),
    ('pt-br', 'Português (Brasil)'),
]

# Caminhos de localização (ajuste conforme sua instalação)
LOCALE_PATHS = [
    '/opt/netbox/netbox/netbox_maintenance_device/locale',  # Docker
    # ou para instalação local:
    # '/caminho/para/seu/netbox/netbox_maintenance_device/locale',
]
```

### 2. Para Docker
Se estiver usando Docker, certifique-se de que o diretório `locale` está sendo copiado corretamente para o container.

### 3. Reiniciar o NetBox
Após fazer as configurações, reinicie o NetBox:

```bash
# Para Docker
docker-compose restart netbox

# Para instalação local
systemctl restart netbox
```

### 4. Verificar no Interface
1. Acesse o NetBox
2. Vá para Device → [qualquer dispositivo]
3. Verifique a aba "Manutenção" - deve estar em português
4. Acesse os formulários de criação - labels devem estar traduzidos

## Estrutura de Arquivos Criada

```
netbox_maintenance_device/
├── locale/
│   └── pt_BR/
│       └── LC_MESSAGES/
│           ├── django.po    # Arquivo fonte de tradução
│           └── django.mo    # Arquivo compilado
├── models.py               # Atualizado com verbose_name
├── forms.py               # Atualizado com imports de tradução
└── __init__.py           # Configurado locale_paths
```

## Scripts Criados

- `compile_po.py` - Script para compilar traduções (caso precise recompilar)
- `django_i18n_config.py` - Exemplo de configurações Django

## Status da Tradução

✅ **COMPLETO** - Todas as strings principais do plugin estão traduzidas
✅ **COMPILADO** - Arquivo .mo gerado com sucesso
✅ **CONFIGURADO** - Plugin configurado para localização

O plugin agora está completamente configurado para português brasileiro!
