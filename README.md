# NetBox Maintenance Device Plugin

[![NetBox](https://img.shields.io/badge/NetBox-4.4%20%7C%204.5%20%7C%204.6%20%7C%204.7-orange)](https://netbox.dev/)
[![PyPI](https://img.shields.io/pypi/v/netbox-maintenance-device)](https://pypi.org/project/netbox-maintenance-device/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/netbox-maintenance-device?period=total&units=ABBREVIATION&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/netbox-maintenance-device)
[![Language](https://img.shields.io/badge/Language-EN%20%7C%20PT--BR-brightgreen)](README.md)

A comprehensive NetBox plugin for managing device preventive and corrective maintenance with enhanced visual indicators, scheduling capabilities, and multi-language support.

![Upcoming & Overdue Maintenance](https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/docs/img/Upcoming.png?raw=true)

## Features

- **Maintenance Plans**: Create and manage maintenance plans for devices **and virtual machines** with configurable frequency
- **Virtual Machine Support**: Plans can target either a `dcim.Device` or a `virtualization.VirtualMachine`, with the same UX on both detail pages (#14)
- **Calendar-based Scheduling**: Schedule every N days / weeks / months / quarters / years, with an optional **calendar anchor** to avoid drift — e.g. "1st day of every month" or "start of each quarter" stays aligned with the calendar regardless of when previous executions happened (#15)
- **Maintenance Executions**: Record and track maintenance executions with status monitoring
- **Device & VM Integration**: View maintenance history directly on device and VM pages with dedicated tabs
- **Quick Actions**: Schedule and complete maintenance directly from the interface
- **Upcoming & Overdue Dashboard**: Filter by status (Overdue / Due Soon / Upcoming / On Track), maintenance type, and target type (Device / VM)
- **REST API**: Complete REST API for external integrations and automation
- **Advanced Filtering**: Powerful filtering and search capabilities
- **Custom Actions**: Schedule, complete, and cancel maintenance via API
- **Statistics**: Get maintenance statistics and overdue/upcoming reports


## Compatibility

| NetBox Version | Plugin Support | Notes |
|----------------|----------------|-------|
| 4.7.x | **Tested & Supported** | Integration tests on 4.7.2 and 4.7.3 |
| 4.6.x | **Tested & Supported** | Regression tests on 4.6.10 |
| 4.5.x | **Tested & Supported** | Regression tests on 4.5.10 |
| 4.4.x | **Tested & Supported** | Regression tests on 4.4.0 and 4.4.10 |
| < 4.4 | **Not Supported** | Below the plugin's minimum version |
| >= 4.8 | **Not Supported** | Requires a separate compatibility review |

> **Note**: Version 1.4.4 supports NetBox 4.4–4.7. See the [NetBox 4.7 compatibility analysis](docs/NETBOX_4.7_COMPATIBILITY.md) for upstream changes, upgrade validation, and test coverage. The configured version range remains bounded to `4.4.0`–`4.7.99`.

> **Python Requirements**: This plugin requires Python 3.12 or later, including on NetBox 4.4. Use the Django and Python versions supported by your NetBox release; NetBox 4.7.3 pins Django 6.1.2.



## Installation

### Method 1: PyPI Installation (Recommended)

**Now officially available on PyPI!**

```bash
# Install the latest version
pip install netbox-maintenance-device

# Or install a specific version
pip install netbox-maintenance-device==1.4.4
```

**For Docker deployments**, add to your `plugin_requirements.txt`:
```bash
echo "netbox-maintenance-device>=1.4.4" >> plugin_requirements.txt
```

### Method 2: GitHub Installation

```bash
# Install from GitHub (development version)
pip install git+https://github.com/diegogodoy06/netbox-maintenance-device.git
```

### Method 3: Docker Installation

For Docker-based NetBox installations using [netbox-docker](https://github.com/netbox-community/netbox-docker):

> **📋 For detailed Docker installation instructions in English and Portuguese, see [DOCKER_INSTALL.md](DOCKER_INSTALL.md)**

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



### Restart Services

Restart your NetBox services:

```bash
# For systemd
sudo systemctl restart netbox netbox-rq

# For Docker
docker compose restart netbox netbox-worker
```

## Usage

For detailed usage instructions, please refer to the **[USAGE.md](USAGE.md)** guide, which includes:

- Creating and managing maintenance plans
- Scheduling and completing maintenance
- Monitoring maintenance status
- Using the REST API
- Troubleshooting common issues

**Quick Start**:
1. Create maintenance plans for your devices
2. View upcoming/overdue maintenance in the dashboard
3. Use quick action buttons to schedule or complete maintenance
4. Monitor device-specific maintenance on device pages

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

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NetBox community for the excellent platform
- Contributors and users providing feedback
