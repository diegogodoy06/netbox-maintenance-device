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
    next_maintenance = tables.Column(empty_values=(), verbose_name='Next Due')
    status = tables.Column(empty_values=(), verbose_name='Status')
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
    next_due = tables.Column(empty_values=(), verbose_name='Next Due', orderable=False)
    days_until = tables.Column(empty_values=(), verbose_name='Days Until Due', orderable=False)
    status = tables.Column(empty_values=(), verbose_name='Status', orderable=False)
    actions = tables.Column(empty_values=(), verbose_name='Actions', orderable=False)
    
    class Meta(NetBoxTable.Meta):
        model = models.MaintenancePlan
        fields = ('pk', 'device', 'name', 'maintenance_type', 'next_due', 
                 'days_until', 'status', 'actions')
        default_columns = ('device', 'name', 'maintenance_type', 'next_due', 
                          'days_until', 'status', 'actions')
    
    def render_next_due(self, record):
        next_date = record.get_next_maintenance_date()
        if next_date:
            return next_date.strftime('%Y-%m-%d')
        return '-'
    
    def render_days_until(self, record):
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
        if record.is_overdue():
            return format_html('<span class="badge badge-danger"><i class="mdi mdi-alert-circle"></i> Overdue</span>')
        
        days_until = record.days_until_due()
        if days_until is not None:
            if days_until <= 7:
                return format_html('<span class="badge badge-warning"><i class="mdi mdi-clock-alert"></i> Due Soon</span>')
            else:
                return format_html('<span class="badge badge-info">Upcoming</span>')
        
        return format_html('<span class="badge badge-success">On Track</span>')
    
    def render_actions(self, record):
        days_until = record.days_until_due()
        if record.is_overdue() or (days_until is not None and days_until <= 7):
            return format_html(
                '<button class="btn btn-sm btn-success quick-complete-btn" '
                'data-plan-id="{}" data-device-id="{}" data-plan-name="{}" '
                'title="Complete Maintenance">'
                '<i class="mdi mdi-check-circle"></i> Complete'
                '</button>',
                record.pk, record.device.pk, record.name
            )
        return '-'