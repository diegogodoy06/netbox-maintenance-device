from netbox.plugins import PluginConfig

class MaintenanceDeviceConfig(PluginConfig):
    name = 'netbox_maintenance_device'
    verbose_name = 'Device Maintenance'
    description = 'Manage device preventive and corrective maintenance'
    version = '1.0.0'
    base_url = 'maintenance-device'
    
    def ready(self):
        super().ready()
        
        # Register device tab
        from dcim.models import Device
        from netbox.plugins.utils import register_template_extensions
        from .template_content import DeviceMaintenanceTab
        
        register_template_extensions([DeviceMaintenanceTab])

config = MaintenanceDeviceConfig