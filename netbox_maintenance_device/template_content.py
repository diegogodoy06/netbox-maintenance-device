from netbox.plugins.utils import PluginTemplateExtension
from dcim.models import Device

class DeviceMaintenanceTab(PluginTemplateExtension):
    model = 'dcim.device'
    
    def left_page(self):
        return self.render('netbox_maintenance_device/device_maintenance_tab.html')