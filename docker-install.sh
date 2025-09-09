#!/bin/bash

# NetBox Maintenance Device Plugin - Docker Installation Script
# Script de Instalação Docker do Plugin NetBox Maintenance Device

set -e

echo "NetBox Maintenance Device Plugin - Docker Installation"
echo "======================================================"
echo "Plugin NetBox Maintenance Device - Instalação Docker"
echo "======================================================"
echo ""

# Check if we're in a netbox-docker directory
if [ ! -f "docker-compose.yml" ] && [ ! -f "docker-compose.yaml" ]; then
    echo "❌ Error: docker-compose.yml not found!"
    echo "❌ Erro: docker-compose.yml não encontrado!"
    echo ""
    echo "Please run this script from your netbox-docker directory."
    echo "Execute este script do diretório netbox-docker."
    exit 1
fi

echo "✅ Found docker-compose.yml"
echo "✅ Encontrado docker-compose.yml"
echo ""

# Check if configuration directory exists
if [ ! -d "configuration" ]; then
    echo "❌ Error: configuration directory not found!"
    echo "❌ Erro: diretório configuration não encontrado!"
    echo ""
    echo "Please ensure you're in the correct netbox-docker directory."
    echo "Certifique-se de estar no diretório netbox-docker correto."
    exit 1
fi

echo "✅ Found configuration directory"
echo "✅ Encontrado diretório configuration"
echo ""

# Add plugin to plugin_requirements.txt
echo "📦 Adding plugin to plugin_requirements.txt..."
echo "📦 Adicionando plugin ao plugin_requirements.txt..."

if ! grep -q "netbox-maintenance-device" plugin_requirements.txt 2>/dev/null; then
    echo "netbox-maintenance-device" >> plugin_requirements.txt
    echo "✅ Added to plugin_requirements.txt"
    echo "✅ Adicionado ao plugin_requirements.txt"
else
    echo "ℹ️  Already present in plugin_requirements.txt"
    echo "ℹ️  Já presente no plugin_requirements.txt"
fi
echo ""

# Check and update plugins.py
echo "⚙️  Checking plugin configuration..."
echo "⚙️  Verificando configuração do plugin..."

PLUGINS_FILE="configuration/plugins.py"

if [ ! -f "$PLUGINS_FILE" ]; then
    echo "📝 Creating plugins.py..."
    echo "📝 Criando plugins.py..."
    cat > "$PLUGINS_FILE" << 'EOF'
# Plugins configuration for NetBox
# Configuração de plugins para NetBox

PLUGINS = [
    'netbox_maintenance_device',
]

# Optional: Plugin-specific configuration
# Opcional: Configuração específica do plugin
PLUGINS_CONFIG = {
    'netbox_maintenance_device': {
        # Plugin-specific settings can be added here in the future
        # Configurações específicas do plugin podem ser adicionadas aqui no futuro
    }
}
EOF
    echo "✅ Created plugins.py with netbox_maintenance_device"
    echo "✅ Criado plugins.py com netbox_maintenance_device"
else
    if ! grep -q "netbox_maintenance_device" "$PLUGINS_FILE"; then
        echo "📝 Adding plugin to existing plugins.py..."
        echo "📝 Adicionando plugin ao plugins.py existente..."
        
        # Backup original file
        cp "$PLUGINS_FILE" "$PLUGINS_FILE.backup"
        
        # Add plugin to PLUGINS list
        if grep -q "PLUGINS.*\[" "$PLUGINS_FILE"; then
            # PLUGINS list exists, add to it
            sed -i "/PLUGINS.*\[/a\\    'netbox_maintenance_device'," "$PLUGINS_FILE"
        else
            # No PLUGINS list, add it
            echo "" >> "$PLUGINS_FILE"
            echo "PLUGINS = [" >> "$PLUGINS_FILE"
            echo "    'netbox_maintenance_device'," >> "$PLUGINS_FILE"
            echo "]" >> "$PLUGINS_FILE"
        fi
        
        echo "✅ Added to existing plugins.py (backup created)"
        echo "✅ Adicionado ao plugins.py existente (backup criado)"
    else
        echo "ℹ️  Already configured in plugins.py"
        echo "ℹ️  Já configurado no plugins.py"
    fi
fi
echo ""

# Rebuild containers
echo "🔨 Rebuilding containers..."
echo "🔨 Reconstruindo containers..."
echo ""

docker compose down
echo ""

echo "Building new images (this may take a few minutes)..."
echo "Construindo novas imagens (isso pode levar alguns minutos)..."
docker compose build --no-cache
echo ""

echo "Starting containers..."
echo "Iniciando containers..."
docker compose up -d
echo ""

# Wait for NetBox to be ready
echo "⏳ Waiting for NetBox to be ready..."
echo "⏳ Aguardando NetBox ficar pronto..."

# Wait up to 60 seconds for NetBox to be ready
for i in {1..12}; do
    if docker compose exec netbox python manage.py check --deploy >/dev/null 2>&1; then
        echo "✅ NetBox is ready!"
        echo "✅ NetBox está pronto!"
        break
    fi
    echo "   Waiting... ($i/12)"
    echo "   Aguardando... ($i/12)"
    sleep 5
done
echo ""

# Run migrations
echo "🗃️  Running database migrations..."
echo "🗃️  Executando migrações do banco de dados..."
docker compose exec netbox python manage.py migrate
echo ""

# Verify installation
echo "🔍 Verifying installation..."
echo "🔍 Verificando instalação..."

if docker compose exec netbox python manage.py shell -c "import netbox_maintenance_device; print('OK')" >/dev/null 2>&1; then
    echo "✅ Plugin installed successfully!"
    echo "✅ Plugin instalado com sucesso!"
else
    echo "❌ Plugin installation failed!"
    echo "❌ Instalação do plugin falhou!"
    echo ""
    echo "Check container logs: docker compose logs netbox"
    echo "Verifique os logs: docker compose logs netbox"
    exit 1
fi
echo ""

echo "🎉 Installation completed successfully!"
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "Next steps / Próximos passos:"
echo "1. Open NetBox web interface / Abra a interface web do NetBox"
echo "2. Navigate to Plugins > Device Maintenance / Navegue para Plugins > Device Maintenance"
echo "3. Start creating maintenance plans! / Comece a criar planos de manutenção!"
echo ""
echo "For more information, see: / Para mais informações, veja:"
echo "- README.md"
echo "- DOCKER_INSTALL.md"