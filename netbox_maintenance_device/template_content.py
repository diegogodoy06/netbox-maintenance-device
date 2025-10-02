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
            
            # Count maintenance status and add pending execution info
            overdue_count = 0
            due_soon_count = 0
            total_active = 0
            
            # Enrich plans with pending execution information
            plans_with_execution = []
            for plan in maintenance_plans:
                # Get pending execution for this plan
                pending_execution = models.MaintenanceExecution.objects.filter(
                    maintenance_plan=plan,
                    status__in=['scheduled', 'in_progress']
                ).order_by('scheduled_date').first()
                
                # Add pending execution as attribute to the plan object
                plan.pending_execution = pending_execution
                plans_with_execution.append(plan)
                
                if plan.is_active:
                    total_active += 1
                    if plan.is_overdue():
                        overdue_count += 1
                    else:
                        days_until = plan.days_until_due()
                        if days_until and days_until <= 7 and days_until > 0:
                            due_soon_count += 1
            
            return {
                'maintenance_plans': plans_with_execution,
                'recent_executions': recent_executions,
                'overdue_count': overdue_count,
                'due_soon_count': due_soon_count,
                'total_active_plans': total_active,
            }
        return {}

template_extensions = [DeviceMaintenanceExtension]