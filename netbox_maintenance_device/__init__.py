from netbox.plugins import PluginConfig
from django.utils.translation import gettext_lazy as _
from netbox.events import (
    EventType, EVENT_TYPE_KIND_WARNING, EVENT_TYPE_KIND_INFO, EVENT_TYPE_KIND_SUCCESS
)
from netbox.registry import registry


class _LazyEventType(EventType):
    """An EventType whose display text may be a lazy translation.

    NetBox's EventType.__str__ returns self.text verbatim, which raises
    TypeError for a gettext_lazy proxy. The event rule detail view renders
    every registered type with {{ event }}, so coerce to str here.
    """

    def __str__(self):
        return str(self.text)


# Registered at module import (NetBox imports plugin packages from its settings
# module while building INSTALLED_APPS) rather than from ready().
#
# EventRuleForm declares `event_types = forms.MultipleChoiceField(
# choices=get_event_type_choices())`, so the list of choices is captured once,
# when extras.forms is first imported. Any plugin that touches extras.forms or
# netbox.views.generic from its own ready() triggers that import, and every
# event type registered after that point -- including all of ours, when the
# other plugin is listed first in PLUGINS -- is missing from the Event Rule
# form's "Event types" dropdown, even though the detail view still lists it
# (that one reads the registry at render time).
#
# The text must stay lazy: gettext() cannot run this early (AppRegistryNotReady).
for _event_type in (
    _LazyEventType('maintenance_due', _('Maintenance due'), kind=EVENT_TYPE_KIND_WARNING),
    _LazyEventType('maintenance_scheduled', _('Maintenance scheduled'), kind=EVENT_TYPE_KIND_INFO),
    _LazyEventType('maintenance_completed', _('Maintenance completed'), kind=EVENT_TYPE_KIND_SUCCESS),
):
    # Assign directly instead of calling .register(), which raises on a
    # duplicate name if the module is ever re-imported.
    registry['event_types'][_event_type.name] = _event_type


class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = _('NetBox Device Maintenance')
    description = 'Manage device preventive and corrective maintenance with multilingual support'
    version = '1.4.3'
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
        
        # Load system jobs to trigger registration
        try:
            import netbox_maintenance_device.jobs  # noqa: F401
            logger.info("NetBox Maintenance Device: Custom system jobs loaded successfully")
        except Exception as e:
            logger.error(f"NetBox Maintenance Device: Custom system jobs load failed: {e}")

        logger.info("NetBox Maintenance Device v1.4.3 initialized successfully")

config = MaintenanceDeviceConfig