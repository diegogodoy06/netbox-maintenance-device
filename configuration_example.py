# NetBox Configuration Example for Maintenance Device Plugin

# Add this to your NetBox configuration.py file:

PLUGINS = [
    'netbox_maintenance_device',
]

# Optional plugin configuration
PLUGINS_CONFIG = {
    'netbox_maintenance_device': {
        # Plugin-specific settings can be added here in the future
        # For now, the plugin uses default settings
    }
}

# The plugin uses standard NetBox permissions, so ensure your users have
# the appropriate permissions:
# - netbox_maintenance_device.view_maintenanceplan
# - netbox_maintenance_device.add_maintenanceplan
# - netbox_maintenance_device.change_maintenanceplan
# - netbox_maintenance_device.delete_maintenanceplan
# - netbox_maintenance_device.view_maintenanceexecution
# - netbox_maintenance_device.add_maintenanceexecution
# - netbox_maintenance_device.change_maintenanceexecution
# - netbox_maintenance_device.delete_maintenanceexecution