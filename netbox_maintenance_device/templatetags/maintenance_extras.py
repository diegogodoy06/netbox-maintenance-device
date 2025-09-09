from django import template
from django.urls import reverse
from ..models import MaintenancePlan

register = template.Library()

@register.inclusion_tag('netbox_maintenance_device/device_maintenance_tab.html', takes_context=True)
def device_maintenance_tab(context, device):
    """Render maintenance tab for device detail view"""
    maintenance_plans = MaintenancePlan.objects.filter(device=device)
    recent_executions = []
    
    for plan in maintenance_plans:
        executions = plan.executions.order_by('-scheduled_date')[:5]
        recent_executions.extend(executions)
    
    # Sort all executions by date
    recent_executions.sort(key=lambda x: x.scheduled_date, reverse=True)
    recent_executions = recent_executions[:10]
    
    return {
        'device': device,
        'maintenance_plans': maintenance_plans,
        'recent_executions': recent_executions,
        'request': context['request'],
        'perms': context['perms'],
    }