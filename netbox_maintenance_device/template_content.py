from netbox.plugins import PluginTemplateExtension
from dcim.models import Device
from . import models

class DeviceMaintenanceExtension(PluginTemplateExtension):
    """Add maintenance information to device detail page"""
    models = ['dcim.device']
    
    def left_page(self):
        """Add maintenance section to the left side of device page"""
        return self.render('netbox_maintenance_device/device_maintenance_section.html', extra_context=self._get_maintenance_context())
    
    def buttons(self):
        """Add maintenance buttons to device page"""
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

template_extensions = [DeviceMaintenanceExtension]