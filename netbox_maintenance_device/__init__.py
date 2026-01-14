from netbox.plugins import PluginConfig
from django.utils.translation import gettext_lazy as _

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = _('NetBox Device Maintenance')
    description = 'Manage device preventive and corrective maintenance with multilingual support'
    version = '1.2.3'
    author = 'Diego Godoy'
    author_email = 'diegoalex-gdy@outlook.com'
    base_url = 'maintenance-device'
    icon = 'mdi-wrench-cog'
    
    # Required NetBox version - Compatible with 4.4.x and 4.5.x
    min_version = '4.4.0'
    max_version = '4.5.99'
    
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
        logger.info("NetBox Maintenance Device v1.2.3 initialized successfully")

config = MaintenanceDeviceConfig