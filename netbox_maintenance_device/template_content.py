from netbox.plugins.utils import TemplateExtension
from dcim.models import Device

class DeviceMaintenanceTab(TemplateExtension):
    model = 'dcim.device'
    
    def left_page(self):
        return self.render('netbox_maintenance_device/device_maintenance_tab.html')