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
        
        # Perform automatic database healing if enabled
        if self.get_config().get('auto_heal_database', True):
            try:
                from .database_healer import auto_heal_database
                auto_heal_database()
            except Exception as e:
                # Don't let auto-healing failures break plugin initialization
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"NetBox Maintenance Device: Auto-healing failed: {e}")

config = MaintenanceDeviceConfig