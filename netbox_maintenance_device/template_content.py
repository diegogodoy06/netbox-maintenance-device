from netbox.plugins import PluginTemplateExtension
from dcim.models import Device
from . import models

class DeviceMaintenanceTab(PluginTemplateExtension):
    models = ['dcim.device']
    
    def left_page(self):
        return self.render('netbox_maintenance_device/device_maintenance_tab.html')
    
    def buttons(self):
        return self.render('netbox_maintenance_device/device_maintenance_buttons.html')

class DeviceMaintenanceTabContent(PluginTemplateExtension):
    models = ['dcim.device']
    
    def detail_tabs(self):
        return [
            {
                'title': 'Maintenance',
                'url': 'netbox_maintenance_device:device_maintenance_tab',
                'permission': 'netbox_maintenance_device.view_maintenanceplan',
                'badge': self._get_maintenance_badge(),
                'hide_if_empty': False
            }
        ]
    
    def _get_maintenance_badge(self):
        """Get badge count for overdue maintenance"""
        if hasattr(self, 'context') and 'object' in self.context:
            device = self.context['object']
            overdue_count = models.MaintenancePlan.objects.filter(
                device=device, 
                is_active=True
            ).filter(
                # Get plans where next maintenance date is in the past
            ).count()
            return overdue_count if overdue_count > 0 else None
        return None

template_extensions = [DeviceMaintenanceTab, DeviceMaintenanceTabContent]