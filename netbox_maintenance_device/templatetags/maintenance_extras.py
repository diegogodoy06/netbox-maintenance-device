from django import template
from django.db.models import Q

from ..models import MaintenancePlan

register = template.Library()


@register.inclusion_tag('netbox_maintenance_device/device_maintenance_tab.html', takes_context=True)
def device_maintenance_tab(context, target):
    """Render maintenance tab for a device or virtual machine detail view."""
    target_filter = Q(device=target) | Q(virtual_machine=target)
    maintenance_plans = MaintenancePlan.objects.filter(target_filter)

    recent_executions = []
    for plan in maintenance_plans:
        recent_executions.extend(plan.executions.order_by('-scheduled_date')[:5])

    recent_executions.sort(key=lambda x: x.scheduled_date, reverse=True)
    recent_executions = recent_executions[:10]

    return {
        'device': target,
        'target': target,
        'maintenance_plans': maintenance_plans,
        'recent_executions': recent_executions,
        'request': context['request'],
        'perms': context['perms'],
    }
