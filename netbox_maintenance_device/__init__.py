from netbox.plugins import PluginConfig
from django.utils.translation import gettext_lazy as _

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = _('NetBox Device Maintenance')
    description = 'Manage device preventive and corrective maintenance with multilingual support'
    version = '1.4.1'
    author = 'Diego Godoy'
    author_email = 'diegoalex-gdy@outlook.com'
    base_url = 'maintenance-device'
    icon = 'mdi-wrench-cog'

    # Required NetBox version - Compatible with 4.4.x, 4.5.x and 4.6.x
    min_version = '4.4.0'
    max_version = '4.6.99'
    
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
        
        # Register custom event types
        try:
            from netbox.events import (
                EventType, EVENT_TYPE_KIND_WARNING, EVENT_TYPE_KIND_INFO, EVENT_TYPE_KIND_SUCCESS
            )
            from django.utils.translation import gettext
            from netbox.registry import registry

            # Overwrite registry directly to avoid duplicate registration errors on reload
            # and use gettext (returning str) instead of gettext_lazy (returning proxy)
            event_types = [
                EventType('maintenance_due', gettext('Maintenance due'), kind=EVENT_TYPE_KIND_WARNING),
                EventType('maintenance_scheduled', gettext('Maintenance scheduled'), kind=EVENT_TYPE_KIND_INFO),
                EventType('maintenance_completed', gettext('Maintenance completed'), kind=EVENT_TYPE_KIND_SUCCESS),
            ]
            for et in event_types:
                registry['event_types'][et.name] = et

            logger.info("NetBox Maintenance Device: Custom event types registered successfully")
        except Exception as e:
            logger.error(f"NetBox Maintenance Device: Custom event types registration failed: {e}")

        # Load system jobs to trigger registration
        try:
            import netbox_maintenance_device.jobs  # noqa: F401
            logger.info("NetBox Maintenance Device: Custom system jobs loaded successfully")
        except Exception as e:
            logger.error(f"NetBox Maintenance Device: Custom system jobs load failed: {e}")

        logger.info("NetBox Maintenance Device v1.4.1 initialized successfully")

config = MaintenanceDeviceConfig