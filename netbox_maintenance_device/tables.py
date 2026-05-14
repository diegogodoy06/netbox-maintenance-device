import django_tables2 as tables
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns

from . import models


def _render_target(record):
    """Render a clickable link to the plan's device or virtual machine."""
    target = record.target
    if target is None:
        return '-'
    return format_html(
        '<a href="{}">{}</a>',
        target.get_absolute_url(),
        target.name,
    )


def _render_target_type(record):
    """Render a short badge identifying the target kind."""
    target_type = record.target_type
    if target_type == 'device':
        return mark_safe(
            '<span class="badge bg-secondary"><i class="mdi mdi-server"></i> Device</span>'
        )
    if target_type == 'virtualmachine':
        return mark_safe(
            '<span class="badge bg-info"><i class="mdi mdi-monitor"></i> VM</span>'
        )
    return '-'


class MaintenancePlanTable(NetBoxTable):
    target = tables.Column(
        empty_values=(),
        verbose_name=_('Target'),
        orderable=False,
    )
    target_type = tables.Column(
        empty_values=(),
        verbose_name=_('Type'),
        orderable=False,
    )
    name = tables.Column(linkify=True)
    maintenance_type = tables.Column()
    frequency = tables.Column(
        empty_values=(),
        verbose_name=_('Frequency'),
        orderable=False,
    )
    anchor_date = tables.Column(verbose_name=_('Anchor'))
    next_maintenance = tables.Column(empty_values=(), verbose_name=_('Next Due'), orderable=False)
    status = tables.Column(empty_values=(), verbose_name=_('Status'), orderable=False)
    is_active = columns.BooleanColumn()

    class Meta(NetBoxTable.Meta):
        model = models.MaintenancePlan
        fields = ('pk', 'target', 'target_type', 'name', 'maintenance_type',
                  'frequency', 'anchor_date', 'next_maintenance', 'status',
                  'is_active', 'created', 'last_updated')
        default_columns = ('target', 'target_type', 'name', 'maintenance_type',
                           'frequency', 'next_maintenance', 'status', 'is_active')

    def render_target(self, record):
        return _render_target(record)

    def render_target_type(self, record):
        return _render_target_type(record)

    def render_frequency(self, record):
        return record.get_frequency_display()

    def render_next_maintenance(self, record):
        next_date = record.get_next_maintenance_date()
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'

    def render_status(self, record):
        if not record.is_active:
            return mark_safe('<span class="badge badge-secondary">Inactive</span>')

        if record.is_overdue():
            return mark_safe('<span class="badge badge-danger">Overdue</span>')

        days_until = record.days_until_due()
        if days_until is not None:
            if days_until <= 7:
                return mark_safe('<span class="badge badge-warning">Due Soon</span>')
            elif days_until <= 30:
                return mark_safe('<span class="badge badge-info">Upcoming</span>')

        return mark_safe('<span class="badge badge-success">On Track</span>')


class MaintenanceExecutionTable(NetBoxTable):
    maintenance_plan = tables.Column(linkify=True)
    target = tables.Column(
        empty_values=(),
        verbose_name=_('Target'),
        orderable=False,
    )
    scheduled_date = columns.DateTimeColumn()
    completed_date = columns.DateTimeColumn()
    status = tables.Column()
    technician = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = models.MaintenanceExecution
        fields = ('pk', 'maintenance_plan', 'target', 'scheduled_date',
                  'completed_date', 'status', 'technician', 'created', 'last_updated')
        default_columns = ('maintenance_plan', 'target', 'scheduled_date',
                           'completed_date', 'status', 'technician')

    def render_target(self, record):
        return _render_target(record.maintenance_plan)


class UpcomingMaintenanceTable(NetBoxTable):
    target = tables.Column(
        empty_values=(),
        verbose_name=_('Target'),
        orderable=False,
    )
    target_type = tables.Column(
        empty_values=(),
        verbose_name=_('Type'),
        orderable=False,
    )
    name = tables.Column(linkify=True)
    maintenance_type = tables.Column()
    frequency = tables.Column(
        empty_values=(),
        verbose_name=_('Frequency'),
        orderable=False,
    )
    next_due = tables.Column(empty_values=(), verbose_name=_('Next Due'), orderable=False)
    days_until = tables.Column(empty_values=(), verbose_name=_('Days Until Due'), orderable=False)
    status = tables.Column(empty_values=(), verbose_name=_('Status'), orderable=False)
    actions = tables.Column(empty_values=(), verbose_name=_('Actions'), orderable=False)

    class Meta(NetBoxTable.Meta):
        model = models.MaintenancePlan
        fields = ('pk', 'target', 'target_type', 'name', 'maintenance_type',
                  'frequency', 'next_due', 'days_until', 'status', 'actions')
        default_columns = ('target', 'target_type', 'name', 'maintenance_type',
                           'frequency', 'next_due', 'days_until', 'status', 'actions')

    def render_target(self, record):
        return _render_target(record)

    def render_target_type(self, record):
        return _render_target_type(record)

    def render_frequency(self, record):
        return record.get_frequency_display()

    def render_next_due(self, record):
        next_date = getattr(record, '_next_due_date', None) or record.get_next_maintenance_date()
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'

    def render_days_until(self, record):
        days = getattr(record, '_days_until', None)
        if days is None:
            days = record.days_until_due()

        if days is not None:
            if days < 0:
                return format_html(
                    '<span class="text-danger">'
                    '<i class="mdi mdi-alert-circle"></i> {} days overdue</span>',
                    abs(days),
                )
            elif days == 0:
                return mark_safe(
                    '<span class="text-warning">'
                    '<i class="mdi mdi-clock-alert"></i> Due today</span>'
                )
            else:
                return f"{days} days"
        return '-'

    def render_status(self, record):
        days = getattr(record, '_days_until', None)
        if days is None:
            days = record.days_until_due()

        if days is not None:
            if days < 0:
                return mark_safe(
                    '<span class="badge badge-danger">'
                    '<i class="mdi mdi-alert-circle"></i> Overdue</span>'
                )
            elif days <= 7:
                return mark_safe(
                    '<span class="badge badge-warning">'
                    '<i class="mdi mdi-clock-alert"></i> Due Soon</span>'
                )
            else:
                return mark_safe('<span class="badge badge-info">Upcoming</span>')

        return mark_safe('<span class="badge badge-success">On Track</span>')

    def render_actions(self, record):
        actions = []
        plan_name = escape(record.name)

        actions.append(
            '<button type="button" class="btn btn-sm btn-outline-primary schedule-btn mr-1 maintenance-action-btn" '
            'data-plan-id="{}" data-plan-name="{}" '
            'title="Schedule Maintenance" '
            'onclick="return false;">'
            '<i class="mdi mdi-calendar-plus"></i> Schedule'
            '</button>'.format(record.pk, plan_name)
        )

        pending_execution = record.executions.filter(
            status__in=['scheduled', 'in_progress']
        ).order_by('scheduled_date').first()

        if pending_execution:
            actions.append(
                '<button type="button" class="btn btn-sm btn-success quick-complete-btn maintenance-action-btn" '
                'data-execution-id="{}" data-plan-name="{}" '
                'title="Complete Scheduled Maintenance" '
                'onclick="return false;">'
                '<i class="mdi mdi-check-circle"></i> Complete'
                '</button>'.format(pending_execution.pk, plan_name)
            )

        return mark_safe(' '.join(actions)) if actions else '-'
