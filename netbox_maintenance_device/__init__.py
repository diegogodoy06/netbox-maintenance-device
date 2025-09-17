from netbox.plugins import PluginConfig

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = 'Netbox Manutenção de Dispositivos'
    description = 'Manage device preventive and corrective maintenance with Portuguese-BR support'
    version = '1.2.1'
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
        'auto_heal_database': True,  # Enable automatic database healing
    }
    
    # Translation configuration
    default_language = 'en'
    locale_paths = ['locale']
    
    def ready(self):
        """
        Called when the plugin is ready. Perform any necessary initialization.
        """
        super().ready()
        
        # Note: Database auto-healing is handled by migrations and model operations
        # to avoid issues during initial Django setup and collectstatic operations
        import logging
        logger = logging.getLogger(__name__)
        logger.info("NetBox Maintenance Device v1.2.1 initialized successfully")

config = MaintenanceDeviceConfig