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
            
            # Count maintenance status
            overdue_count = 0
            due_soon_count = 0
            total_active = 0
            
            for plan in maintenance_plans:
                if plan.is_active:
                    total_active += 1
                    if plan.is_overdue():
                        overdue_count += 1
                    else:
                        days_until = plan.days_until_due()
                        if days_until and days_until <= 7 and days_until > 0:
                            due_soon_count += 1
            
            return {
                'maintenance_plans': maintenance_plans,
                'recent_executions': recent_executions,
                'overdue_count': overdue_count,
                'due_soon_count': due_soon_count,
                'total_active_plans': total_active,
            }
        return {}

from netbox.plugins import PluginTemplateExtension
from dcim.models import Device
from . import models

class DeviceMaintenanceExtension(PluginTemplateExtension):
    """Add maintenance information to device detail page"""
    model = 'dcim.device'
    
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
            
            # Count maintenance status
            overdue_count = 0
            due_soon_count = 0
            total_active = 0
            
            for plan in maintenance_plans:
                if plan.is_active:
                    total_active += 1
                    if plan.is_overdue():
                        overdue_count += 1
                    else:
                        days_until = plan.days_until_due()
                        if days_until and days_until <= 7 and days_until > 0:
                            due_soon_count += 1
            
            return {
                'maintenance_plans': maintenance_plans,
                'recent_executions': recent_executions,
                'overdue_count': overdue_count,
                'due_soon_count': due_soon_count,
                'total_active_plans': total_active,
            }
        return {}


class MaintenanceNotificationExtension(PluginTemplateExtension):
    """Add notification indicator to navbar"""
    model = 'dcim.device'
    
    def navbar(self):
        """Add notification indicator to navbar"""
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            unread_count = models.MaintenanceNotification.objects.filter(
                user=self.request.user,
                is_read=False
            ).count()
            
            context = {
                'unread_count': unread_count,
                'user': self.request.user
            }
            
            return self.render('netbox_maintenance_device/notification_indicator.html', extra_context=context)
        return ""


template_extensions = [DeviceMaintenanceExtension, MaintenanceNotificationExtension]