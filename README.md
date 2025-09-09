# NetBox Maintenance Device Plugin

A NetBox plugin for managing device preventive and corrective maintenance.

## Features

- **Maintenance Plans**: Create maintenance plans for devices with configurable frequency
- **Maintenance Executions**: Record and track maintenance executions
- **Device Integration**: View maintenance history directly on device pages
- **Dashboard**: Monitor upcoming and overdue maintenance
- **Types**: Support for both preventive and corrective maintenance
- **Status Tracking**: Track maintenance status from scheduled to completed

## Installation

### Standard Installation

1. Install the plugin:
```bash
pip install netbox-maintenance-device
```

2. Add to NetBox configuration (`configuration.py`):
```python
PLUGINS = [
    'netbox_maintenance_device',
]
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Restart NetBox services.

### Docker Installation (netbox-docker)

For Docker-based NetBox installations using [netbox-docker](https://github.com/netbox-community/netbox-docker):

> **📋 For detailed Docker installation instructions in English and Portuguese, see [DOCKER_INSTALL.md](DOCKER_INSTALL.md)**

#### Quick Start

1. Add the plugin to `plugin_requirements.txt` in your netbox-docker directory:
```bash
echo "netbox-maintenance-device" >> plugin_requirements.txt
```

2. Configure the plugin in `configuration/plugins.py`:
```python
PLUGINS = [
    'netbox_maintenance_device',
]
```

3. Rebuild and restart:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose exec netbox python manage.py migrate
```

### Instalação Docker (netbox-docker) - Guia Rápido

Para instalações do NetBox baseadas em Docker usando [netbox-docker](https://github.com/netbox-community/netbox-docker):

> **📋 Para instruções detalhadas de instalação Docker em português e inglês, veja [DOCKER_INSTALL.md](DOCKER_INSTALL.md)**

#### Início Rápido

1. Adicione o plugin ao `plugin_requirements.txt` no diretório netbox-docker:
```bash
echo "netbox-maintenance-device" >> plugin_requirements.txt
```

2. Configure o plugin em `configuration/plugins.py`:
```python
PLUGINS = [
    'netbox_maintenance_device',
]
```

3. Reconstrua e reinicie:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose exec netbox python manage.py migrate
```

## Usage

### Creating Maintenance Plans

1. Navigate to **Plugins > Device Maintenance > Maintenance Plans**
2. Click **Add** to create a new maintenance plan
3. Select a device, provide a name, and set the frequency in days
4. Choose between preventive or corrective maintenance type

### Recording Maintenance Executions

1. Navigate to **Plugins > Device Maintenance > Maintenance Executions**
2. Click **Add** to record a new maintenance execution
3. Select the maintenance plan and set the scheduled/completed dates
4. Update status and add notes as needed

### Viewing Device Maintenance

On any device detail page, you'll see a **Maintenance** section showing:
- Active maintenance plans for the device
- Recent maintenance history
- Next due dates and status indicators

### Monitoring Upcoming Maintenance

Use **Plugins > Device Maintenance > Upcoming Maintenance** to view:
- All maintenance due within 30 days
- Overdue maintenance items
- Status indicators for quick prioritization

## Models

### MaintenancePlan
- Links to a specific device
- Defines maintenance type (preventive/corrective)
- Sets frequency in days
- Can be activated/deactivated

### MaintenanceExecution  
- Records actual maintenance performed
- Tracks scheduled vs completed dates
- Includes status, technician, and notes
- Links back to the maintenance plan

## Permissions

The plugin uses standard NetBox permissions:
- `netbox_maintenance_device.view_maintenanceplan`
- `netbox_maintenance_device.add_maintenanceplan`
- `netbox_maintenance_device.change_maintenanceplan`
- `netbox_maintenance_device.delete_maintenanceplan`
- `netbox_maintenance_device.view_maintenanceexecution`
- `netbox_maintenance_device.add_maintenanceexecution`
- `netbox_maintenance_device.change_maintenanceexecution`
- `netbox_maintenance_device.delete_maintenanceexecution`