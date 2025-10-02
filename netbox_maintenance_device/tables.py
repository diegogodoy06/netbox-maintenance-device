import django_tables2 as tables
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from netbox.tables import NetBoxTable, columns
from . import models


class MaintenancePlanTable(NetBoxTable):
    device = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    maintenance_type = tables.Column()
    frequency_days = tables.Column(verbose_name='Frequency (days)')
    next_maintenance = tables.Column(empty_values=(), verbose_name='Next Due', orderable=False)
    status = tables.Column(empty_values=(), verbose_name='Status', orderable=False)
    is_active = columns.BooleanColumn()
    
    class Meta(NetBoxTable.Meta):
        model = models.MaintenancePlan
        fields = ('pk', 'device', 'name', 'maintenance_type', 'frequency_days', 
                 'next_maintenance', 'status', 'is_active', 'created', 'last_updated')
        default_columns = ('device', 'name', 'maintenance_type', 'frequency_days', 
                          'next_maintenance', 'status', 'is_active')
    
    def render_next_maintenance(self, record):
        next_date = record.get_next_maintenance_date()
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'
    
    def render_status(self, record):
        if not record.is_active:
            return format_html('<span class="badge badge-secondary">Inactive</span>')
        
        if record.is_overdue():
            return format_html('<span class="badge badge-danger">Overdue</span>')
        
        days_until = record.days_until_due()
        if days_until is not None:
            if days_until <= 7:
                return format_html('<span class="badge badge-warning">Due Soon</span>')
            elif days_until <= 30:
                return format_html('<span class="badge badge-info">Upcoming</span>')
        
        return format_html('<span class="badge badge-success">On Track</span>')


class MaintenanceExecutionTable(NetBoxTable):
    maintenance_plan = tables.Column(linkify=True)
    device = tables.Column(accessor='maintenance_plan.device', linkify=True)
    scheduled_date = columns.DateTimeColumn()
    completed_date = columns.DateTimeColumn()
    status = tables.Column()
    technician = tables.Column()
    
    class Meta(NetBoxTable.Meta):
        model = models.MaintenanceExecution
        fields = ('pk', 'maintenance_plan', 'device', 'scheduled_date', 
                 'completed_date', 'status', 'technician', 'created', 'last_updated')
        default_columns = ('maintenance_plan', 'device', 'scheduled_date', 
                          'completed_date', 'status', 'technician')


class UpcomingMaintenanceTable(NetBoxTable):
    device = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    maintenance_type = tables.Column()
    next_due = tables.Column(empty_values=(), verbose_name='Next Due', order_by='_next_due_date')
    days_until = tables.Column(empty_values=(), verbose_name='Days Until Due', order_by='_days_until')
    status = tables.Column(empty_values=(), verbose_name='Status', order_by='_status_priority')
    actions = tables.Column(empty_values=(), verbose_name='Actions', orderable=False)
    
    class Meta(NetBoxTable.Meta):
        model = models.MaintenancePlan
        fields = ('pk', 'device', 'name', 'maintenance_type', 'next_due', 
                 'days_until', 'status', 'actions')
        default_columns = ('device', 'name', 'maintenance_type', 'next_due', 
                          'days_until', 'status', 'actions')
    
    def render_next_due(self, record):
        # Try to use annotated field first, fallback to method
        if hasattr(record, '_next_due_date') and record._next_due_date:
            return record._next_due_date.strftime('%Y-%m-%d')
        
        next_date = record.get_next_maintenance_date()
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'
    
    def render_days_until(self, record):
        # Try to use annotated field first, fallback to method
        if hasattr(record, '_days_until'):
            days = record._days_until
        else:
            days = record.days_until_due()
        
        if days is not None:
            if days < 0:
                return format_html('<span class="text-danger"><i class="mdi mdi-alert-circle"></i> {} days overdue</span>', abs(days))
            elif days == 0:
                return format_html('<span class="text-warning"><i class="mdi mdi-clock-alert"></i> Due today</span>')
            else:
                return f"{days} days"
        return '-'
    
    def render_status(self, record):
        # Use annotated field if available, otherwise calculate
        if hasattr(record, '_days_until'):
            days = record._days_until
        else:
            days = record.days_until_due()
        
        if days is not None:
            if days < 0:
                return format_html('<span class="badge badge-danger"><i class="mdi mdi-alert-circle"></i> Overdue</span>')
            elif days <= 7:
                return format_html('<span class="badge badge-warning"><i class="mdi mdi-clock-alert"></i> Due Soon</span>')
            else:
                return format_html('<span class="badge badge-info">Upcoming</span>')
        
        return format_html('<span class="badge badge-success">On Track</span>')
    
    def render_actions(self, record):
        from django.utils.html import escape
        actions = []
        
        # Use annotated field if available, otherwise calculate
        if hasattr(record, '_days_until'):
            days_until = record._days_until
        else:
            days_until = record.days_until_due()
        
        # Escape plan name to prevent issues with special characters
        plan_name = escape(record.name)
        
        # Schedule button - sempre disponível para planos ativos
        actions.append(
            '<button type="button" class="btn btn-sm btn-outline-primary schedule-btn mr-1 maintenance-action-btn" '
            'data-plan-id="{}" data-plan-name="{}" '
            'title="Schedule Maintenance" '
            'onclick="return false;">'
            '<i class="mdi mdi-calendar-plus"></i> Schedule'
            '</button>'.format(record.pk, plan_name)
        )
        
        # Complete button - apenas se houver agendamento pendente (scheduled ou in_progress)
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
        
        return format_html(' '.join(actions)) if actions else '-'