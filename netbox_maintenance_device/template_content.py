from netbox.plugins import PluginTemplateExtension
from dcim.models import Device
from . import models

class DeviceMaintenanceTab(PluginTemplateExtension):
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
    
    def buttons(self):
        return self.render('netbox_maintenance_device/device_maintenance_buttons.html', extra_context=self._get_maintenance_context())
    
    def _get_maintenance_context(self):
        """Get maintenance context for the device"""
        if hasattr(self, 'context') and 'object' in self.context:
            device = self.context['object']
            maintenance_plans = models.MaintenancePlan.objects.filter(device=device)
            recent_executions = models.MaintenanceExecution.objects.filter(
                maintenance_plan__device=device
            ).order_by('-scheduled_date')[:5]
            
            # Count overdue maintenance
            overdue_count = sum(1 for plan in maintenance_plans if plan.is_overdue())
            
            return {
                'maintenance_plans': maintenance_plans,
                'recent_executions': recent_executions,
                'overdue_count': overdue_count,
            }
        return {}
    
    def _get_maintenance_badge(self):
        """Get badge count for overdue maintenance"""
        context = self._get_maintenance_context()
        overdue_count = context.get('overdue_count', 0)
        return overdue_count if overdue_count > 0 else None

template_extensions = [DeviceMaintenanceTab]