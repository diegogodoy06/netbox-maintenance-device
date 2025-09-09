from netbox.plugins import PluginConfig

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = 'Device Maintenance'
    description = 'Manage device preventive and corrective maintenance'
    version = '1.0.0'
    base_url = 'maintenance-device'

config = MaintenanceDeviceConfig