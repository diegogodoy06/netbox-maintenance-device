# Installation Summary - Resumo da Instalação

## Quick Installation for Docker / Instalação Rápida para Docker

### Automated Installation / Instalação Automatizada

Run the automated script from your netbox-docker directory:
```bash
curl -sSL https://raw.githubusercontent.com/diegogodoy06/netbox-maintenance-device/main/docker-install.sh | bash
```

Or download and run locally:
```bash
wget https://raw.githubusercontent.com/diegogodoy06/netbox-maintenance-device/main/docker-install.sh
chmod +x docker-install.sh
./docker-install.sh
```

Execute o script automatizado do diretório netbox-docker:
```bash
curl -sSL https://raw.githubusercontent.com/diegogodoy06/netbox-maintenance-device/main/docker-install.sh | bash
```

Ou baixe e execute localmente:
```bash
wget https://raw.githubusercontent.com/diegogodoy06/netbox-maintenance-device/main/docker-install.sh
chmod +x docker-install.sh
./docker-install.sh
```

### Manual Installation / Instalação Manual

1. **Add to plugin_requirements.txt:**
```bash
echo "netbox-maintenance-device" >> plugin_requirements.txt
```

2. **Configure in configuration/plugins.py:**
```python
PLUGINS = ['netbox_maintenance_device']
```

3. **Rebuild containers:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose exec netbox python manage.py migrate
```

## Documentation Files / Arquivos de Documentação

- `DOCKER_INSTALL.md` - Complete Docker installation guide (English/Portuguese)
- `README.md` - Updated with Docker quick start section
- `docker-install.sh` - Automated installation script
- `plugin_requirements.txt` - Example requirements file
- `docker-compose.override.yml.example` - Docker Compose override example
- `Dockerfile.override.example` - Custom Dockerfile example

## Verification / Verificação

After installation, verify the plugin is working:

1. Access NetBox web interface
2. Navigate to **Plugins > Device Maintenance**
3. You should see menu options for maintenance plans and executions

Após a instalação, verifique se o plugin está funcionando:

1. Acesse a interface web do NetBox
2. Navegue para **Plugins > Device Maintenance**
3. Você deve ver opções de menu para planos e execuções de manutenção

## Support / Suporte

For issues or questions:
- Check `DOCKER_INSTALL.md` for detailed troubleshooting
- Review container logs: `docker compose logs netbox`
- Verify plugin installation: `docker compose exec netbox pip list | grep netbox-maintenance-device`

Para problemas ou dúvidas:
- Verifique `DOCKER_INSTALL.md` para solução de problemas detalhada
- Revise os logs do container: `docker compose logs netbox`
- Verifique a instalação do plugin: `docker compose exec netbox pip list | grep netbox-maintenance-device`