from netbox.plugins import PluginConfig

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = 'Netbox Manutenção de Dispositivos'
    description = 'Manage device preventive and corrective maintenance'
    version = '1.2.0'
    author = 'Diego Godoy'
    author_email = 'diegoalex-gdy@outlook.com'
    base_url = 'maintenance-device'
    icon = 'mdi-wrench-cog'
    
    # Required NetBox version
    min_version = '4.0.0'
    max_version = '4.9.0'
    
    # Default configurations
    default_settings = {
        'default_frequency_days': 30,
    }
    
    # Translation configuration
    default_language = 'en'
    locale_paths = ['locale']

config = MaintenanceDeviceConfig

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = 'Netbox Manutenção de Dispositivos'
    description = 'Manage device preventive and corrective maintenance with Portuguese-BR support'
    version = '1.1.0'
    base_url = 'maintenance-device'
    icon = 'mdi-wrench-cog'
    
    # Default configurations
    default_settings = {
        'default_frequency_days': 30,
    }
    
    # Translation configuration
    default_language = 'en'
    locale_paths = ['locale']

config = MaintenanceDeviceConfig