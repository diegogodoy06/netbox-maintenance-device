# NetBox Maintenance Device Plugin

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![NetBox](https://img.shields.io/badge/NetBox-4.0%2B-orange)](https://netbox.dev/)
[![Language](https://img.shields.io/badge/Language-EN%20%7C%20PT--BR-brightgreen)](README.md)

A comprehensive NetBox plugin for managing device preventive and corrective maintenance with enhanced visual indicators, scheduling capabilities, and multi-language support.

![Upcoming & Overdue Maintenance](https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/docs/img/Upcoming.png?raw=true)

## Features

- **Maintenance Plans**: Create and manage maintenance plans for devices with configurable frequency
- **Maintenance Executions**: Record and track maintenance executions with status monitoring
- **Device Integration**: View maintenance history directly on device pages with dedicated tabs
- **Quick Actions**: Schedule and complete maintenance directly from the interface


## Compatibility

| NetBox Version | Plugin Support |
|----------------|----------------|
| 4.4.x | ✅ |
| 4.3.x | ✅ |
| 4.2.x | ✅ |
| 4.1.x | ✅ |
| 4.0.x | ✅ |
| 3.x | ❌ |



## Installation

### Method 1: PyPI Installation (Recommended)

```bash
pip install netbox-maintenance-device
```

### Method 2: GitHub Installation

```bash
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
```

### Method 3: Docker Installation

For Docker-based NetBox installations using [netbox-docker](https://github.com/netbox-community/netbox-docker):

> **📋 For detailed Docker installation instructions in English and Portuguese, see [DOCKER_INSTALL.md](DOCKER_INSTALL.md)**

#### Quick Docker Setup

1. Add to `plugin_requirements.txt`:
```bash
echo "https://github.com/diegogodoy06/netbox-maintenance-device/archive/main.tar.gz" >> plugin_requirements.txt
```

2. Configure in `configuration/plugins.py`:
```python
PLUGINS = ['netbox_maintenance_device']
```

3. Rebuild and restart:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose exec netbox python manage.py migrate
```

## Configuration

### Basic Configuration

Add the plugin to your NetBox `configuration.py`:

```python
# configuration.py

PLUGINS = [
    'netbox_maintenance_device',
    # ... other plugins
]

# Optional: Plugin-specific settings
PLUGINS_CONFIG = {
    'netbox_maintenance_device': {
        # Future configuration options will be added here
        # Currently, the plugin uses default settings
    }
}
```

### Language Configuration (Optional)

To enable Portuguese-BR by default:

```python
# configuration.py

# Enable internationalization
USE_I18N = True
USE_L10N = True

# Set default language
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

# Available languages
LANGUAGES = [
    ('en', 'English'),
    ('pt-br', 'Português (Brasil)'),
]
```

### Database Migration

After configuration, run migrations:

```bash
python manage.py migrate
```

### Restart Services

Restart your NetBox services:

```bash
# For systemd
sudo systemctl restart netbox netbox-rq

# For Docker
docker compose restart netbox netbox-worker
```

## Screenshots

### Device Maintenance Section
*View maintenance plans and status directly on device pages*

![Device Maintenance](https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/docs/img/device.png?raw=true)

### Upcoming Maintenance Dashboard
*Monitor all upcoming and overdue maintenance across your infrastructure*

![Upcoming Maintenance](https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/docs/img/Upcoming.png?raw=true)

### Maintenance Plan Management
*Create and manage maintenance plans with flexible scheduling*

![Maintenance Plans](https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/docs/img/Plans.png?raw=true)


##  Usage

### Creating Maintenance Plans

1. Navigate to **Plugins > Manutenção de Dispositivos > Planos de Manutenção**
2. Click **Add** to create a new maintenance plan
3. Select a device, provide a name, and set the frequency in days
4. Choose between preventive or corrective maintenance type
5. Save and activate the plan

### Scheduling Maintenance

#### From Device Page:
1. Go to any device detail page
2. View the **Maintenance** section
3. Click the **📅 Schedule** button next to any plan
4. Set date, technician, and notes
5. Confirm to create a scheduled execution

#### From Upcoming Maintenance:
1. Navigate to **Plugins > Upcoming Maintenance**
2. Find the maintenance plan in the table
3. Click **📅 Schedule** in the Actions column
4. Complete the scheduling form

### Completing Maintenance

#### Quick Complete:
1. From the **Upcoming Maintenance** page or device section
2. Click the **✅ Complete** button for overdue/due maintenance
3. Add technician notes and confirm
4. The system creates and marks the execution as completed

#### Manual Recording:
1. Navigate to **Plugins > Maintenance Executions**
2. Click **Add** to record a new execution
3. Select the plan, set dates, and update status
4. Add detailed notes and technician information

### Monitoring Maintenance

#### Device-Level Monitoring:
- **Maintenance Section**: Shows active plans with status badges
- **Visual Indicators**: Red (overdue), yellow (due soon), green (on track)
- **Quick Actions**: Schedule and complete buttons for urgent items

#### Dashboard Monitoring:
- **Upcoming Maintenance**: Centralized view of all maintenance
- **Status Filters**: Filter by overdue, due soon, or scheduled
- **Bulk Actions**: Manage multiple maintenance items efficiently

## Models

### MaintenancePlan
- **Device**: Links to a specific NetBox device
- **Name**: Descriptive name for the maintenance type
- **Type**: Preventive or corrective maintenance
- **Frequency**: Maintenance interval in days
- **Status**: Active/inactive flag

### MaintenanceExecution
- **Plan**: Links to the maintenance plan
- **Scheduled Date**: When maintenance is scheduled
- **Completed Date**: When maintenance was completed
- **Status**: scheduled, in_progress, completed, cancelled
- **Technician**: Person responsible for maintenance
- **Notes**: Detailed maintenance notes


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NetBox community for the excellent platform
- Contributors and users providing feedback
