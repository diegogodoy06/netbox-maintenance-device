# Docker Installation Guide - Guia de Instalação para Docker

Este guia fornece instruções detalhadas para instalar o plugin NetBox Maintenance Device em um ambiente Docker usando netbox-docker.

This guide provides detailed instructions for installing the NetBox Maintenance Device plugin in a Docker environment using netbox-docker.

## Prerequisites - Pré-requisitos

- Docker and Docker Compose installed / Docker e Docker Compose instalados
- Running netbox-docker installation / Instalação do netbox-docker em execução
- Administrative access to modify configuration files / Acesso administrativo para modificar arquivos de configuração

## Installation Methods - Métodos de Instalação

### Method 1: plugin_requirements.txt (Recommended)

#### English

This is the preferred method as it integrates with the standard netbox-docker plugin installation mechanism.

1. **Navigate to your netbox-docker directory:**
```bash
cd /path/to/your/netbox-docker
```

2. **Add the plugin to plugin_requirements.txt:**
```bash
echo "netbox-maintenance-device" >> plugin_requirements.txt
```

3. **Configure the plugin:**
Edit the file `configuration/plugins.py` and add:
```python
PLUGINS = [
    'netbox_maintenance_device',
]

# Optional: Plugin configuration
PLUGINS_CONFIG = {
    'netbox_maintenance_device': {
        # Plugin-specific settings can be added here in the future
    }
}
```

4. **Rebuild the containers:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

5. **Run database migrations:**
```bash
docker compose exec netbox python manage.py migrate
```

6. **Verify installation:**
```bash
docker compose exec netbox python manage.py shell -c "import netbox_maintenance_device; print('Plugin loaded successfully')"
```

#### Português

Este é o método preferido, pois se integra com o mecanismo padrão de instalação de plugins do netbox-docker.

1. **Navegue até o diretório do netbox-docker:**
```bash
cd /caminho/para/seu/netbox-docker
```

2. **Adicione o plugin ao plugin_requirements.txt:**
```bash
echo "netbox-maintenance-device" >> plugin_requirements.txt
```

3. **Configure o plugin:**
Edite o arquivo `configuration/plugins.py` e adicione:
```python
PLUGINS = [
    'netbox_maintenance_device',
]

# Opcional: Configuração do plugin
PLUGINS_CONFIG = {
    'netbox_maintenance_device': {
        # Configurações específicas do plugin podem ser adicionadas aqui no futuro
    }
}
```

4. **Reconstrua os containers:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

5. **Execute as migrações do banco de dados:**
```bash
docker compose exec netbox python manage.py migrate
```

6. **Verifique a instalação:**
```bash
docker compose exec netbox python manage.py shell -c "import netbox_maintenance_device; print('Plugin carregado com sucesso')"
```

### Method 2: Custom Dockerfile

#### English

Use this method if you need more control over the installation process.

1. **Create a custom Dockerfile:**
Create `Dockerfile.override` in your netbox-docker directory:
```dockerfile
FROM netboxcommunity/netbox:latest

# Install the plugin
RUN pip install netbox-maintenance-device

# Optional: Install additional dependencies if needed
# RUN pip install additional-package
```

2. **Update docker-compose.override.yml:**
```yaml
version: '3.4'
services:
  netbox:
    build:
      context: .
      dockerfile: Dockerfile.override
  netbox-worker:
    build:
      context: .
      dockerfile: Dockerfile.override
  netbox-housekeeping:
    build:
      context: .
      dockerfile: Dockerfile.override
```

3. **Configure the plugin** (same as Method 1, step 3)

4. **Build and start containers:**
```bash
docker compose up -d --build
```

5. **Run migrations:**
```bash
docker compose exec netbox python manage.py migrate
```

#### Português

Use este método se precisar de mais controle sobre o processo de instalação.

1. **Crie um Dockerfile personalizado:**
Crie `Dockerfile.override` no diretório do netbox-docker:
```dockerfile
FROM netboxcommunity/netbox:latest

# Instale o plugin
RUN pip install netbox-maintenance-device

# Opcional: Instale dependências adicionais se necessário
# RUN pip install pacote-adicional
```

2. **Atualize docker-compose.override.yml:**
```yaml
version: '3.4'
services:
  netbox:
    build:
      context: .
      dockerfile: Dockerfile.override
  netbox-worker:
    build:
      context: .
      dockerfile: Dockerfile.override
  netbox-housekeeping:
    build:
      context: .
      dockerfile: Dockerfile.override
```

3. **Configure o plugin** (mesmo que Método 1, passo 3)

4. **Construa e inicie os containers:**
```bash
docker compose up -d --build
```

5. **Execute as migrações:**
```bash
docker compose exec netbox python manage.py migrate
```

## Verification - Verificação

### Web Interface - Interface Web

1. Access your NetBox web interface / Acesse a interface web do NetBox
2. Navigate to **Plugins > Device Maintenance** / Navegue para **Plugins > Device Maintenance**
3. You should see the following menu items / Você deve ver os seguintes itens de menu:
   - **Upcoming Maintenance** - Manutenções Próximas
   - **Maintenance Plans** - Planos de Manutenção  
   - **Maintenance Executions** - Execuções de Manutenção

### Command Line - Linha de Comando

Check if the plugin is properly loaded:
```bash
docker compose exec netbox python manage.py shell -c "
from django.conf import settings
print('Installed plugins:', settings.PLUGINS)
"
```

Verificar se o plugin está carregado corretamente:
```bash
docker compose exec netbox python manage.py shell -c "
from django.conf import settings
print('Plugins instalados:', settings.PLUGINS)
"
```

## Troubleshooting - Solução de Problemas

### Common Issues - Problemas Comuns

#### Plugin not appearing in menu / Plugin não aparece no menu

1. **Check container logs / Verifique os logs do container:**
```bash
docker compose logs netbox
```

2. **Verify plugin installation / Verifique a instalação do plugin:**
```bash
docker compose exec netbox pip list | grep netbox-maintenance-device
```

3. **Check configuration / Verifique a configuração:**
```bash
docker compose exec netbox python manage.py shell -c "
from django.conf import settings
print('PLUGINS:', getattr(settings, 'PLUGINS', 'Not configured'))
"
```

#### Migration errors / Erros de migração

1. **Check for pending migrations / Verifique migrações pendentes:**
```bash
docker compose exec netbox python manage.py showmigrations netbox_maintenance_device
```

2. **Run migrations manually / Execute migrações manualmente:**
```bash
docker compose exec netbox python manage.py migrate netbox_maintenance_device
```

#### Permission errors / Erros de permissão

1. **Create a superuser / Crie um superusuário:**
```bash
docker compose exec netbox python manage.py createsuperuser
```

2. **Assign plugin permissions / Atribua permissões do plugin:**
   - Log into NetBox as superuser / Entre no NetBox como superusuário
   - Go to **Admin > Users & Groups > Users** / Vá para **Admin > Users & Groups > Users**
   - Edit user and assign maintenance device permissions / Edite o usuário e atribua permissões do dispositivo de manutenção

### Getting Help - Obtendo Ajuda

If you encounter issues not covered here:
- Check the [main README](README.md) for general usage information
- Review NetBox and netbox-docker documentation
- Check container logs for detailed error messages

Se encontrar problemas não cobertos aqui:
- Verifique o [README principal](README.md) para informações gerais de uso
- Revise a documentação do NetBox e netbox-docker
- Verifique os logs do container para mensagens de erro detalhadas

## Uninstalling - Desinstalação

To remove the plugin / Para remover o plugin:

1. **Remove from configuration / Remova da configuração:**
Edit `configuration/plugins.py` and remove the plugin from PLUGINS list.

2. **Remove from requirements / Remova dos requisitos:**
```bash
# For Method 1
sed -i '/netbox-maintenance-device/d' plugin_requirements.txt

# For Method 2
# Remove the RUN pip install line from Dockerfile.override
```

3. **Rebuild containers / Reconstrua os containers:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Note:** Database tables created by the plugin will remain. To remove them completely, you would need to create and run reverse migrations.

**Nota:** As tabelas do banco de dados criadas pelo plugin permanecerão. Para removê-las completamente, você precisaria criar e executar migrações reversas.