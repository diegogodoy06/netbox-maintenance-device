from netbox.plugins import PluginTemplateExtension

from . import models


class _MaintenanceExtensionMixin:
    """Shared logic for surfacing maintenance info on device / VM detail pages."""

    target_kwarg = None  # 'device' or 'virtual_machine'
    tab_url_name = None  # URL name for the dedicated maintenance tab page

    def _get_maintenance_context(self):
        target = self.context.get('object') if hasattr(self, 'context') else None
        if target is None:
            return {}

        plan_filter = {self.target_kwarg: target}
        execution_filter = {f'maintenance_plan__{self.target_kwarg}': target}

        maintenance_plans = list(models.MaintenancePlan.objects.filter(**plan_filter))
        recent_executions = models.MaintenanceExecution.objects.filter(
            **execution_filter
        ).order_by('-scheduled_date')[:5]

        overdue_count = 0
        due_soon_count = 0
        total_active = 0

        plans_with_execution = []
        for plan in maintenance_plans:
            pending_execution = models.MaintenanceExecution.objects.filter(
                maintenance_plan=plan,
                status__in=['scheduled', 'in_progress']
            ).order_by('scheduled_date').first()

            plan.pending_execution = pending_execution
            plans_with_execution.append(plan)

            if plan.is_active:
                total_active += 1
                if plan.is_overdue():
                    overdue_count += 1
                else:
                    days_until = plan.days_until_due()
                    if days_until and 0 < days_until <= 7:
                        due_soon_count += 1

        return {
            'maintenance_plans': plans_with_execution,
            'recent_executions': recent_executions,
            'overdue_count': overdue_count,
            'due_soon_count': due_soon_count,
            'total_active_plans': total_active,
            'target_kwarg': self.target_kwarg,
            'maintenance_tab_url_name': self.tab_url_name,
        }

    def left_page(self):
        return self.render(
            'netbox_maintenance_device/device_maintenance_section.html',
            extra_context=self._get_maintenance_context(),
        )

    def buttons(self):
        return self.render(
            'netbox_maintenance_device/device_maintenance_buttons.html',
            extra_context=self._get_maintenance_context(),
        )


class DeviceMaintenanceExtension(_MaintenanceExtensionMixin, PluginTemplateExtension):
    """Add maintenance info to the device detail page."""
    models = ['dcim.device']
    target_kwarg = 'device'
    tab_url_name = 'plugins:netbox_maintenance_device:device_maintenance_tab'


class VirtualMachineMaintenanceExtension(_MaintenanceExtensionMixin, PluginTemplateExtension):
    """Add maintenance info to the virtual machine detail page."""
    models = ['virtualization.virtualmachine']
    target_kwarg = 'virtual_machine'
    tab_url_name = 'plugins:netbox_maintenance_device:virtualmachine_maintenance_tab'


template_extensions = [
    DeviceMaintenanceExtension,
    VirtualMachineMaintenanceExtension,
]
