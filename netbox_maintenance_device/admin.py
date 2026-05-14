from django.contrib import admin

from . import models


@admin.register(models.MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'device', 'virtual_machine', 'maintenance_type',
        'frequency_days', 'frequency_unit', 'anchor_date', 'is_active', 'created',
    ]
    list_filter = ['maintenance_type', 'frequency_unit', 'is_active', 'created']
    search_fields = ['device__name', 'virtual_machine__name', 'name', 'description']
    ordering = ['device', 'virtual_machine', 'name']


@admin.register(models.MaintenanceExecution)
class MaintenanceExecutionAdmin(admin.ModelAdmin):
    list_display = ['maintenance_plan', 'scheduled_date', 'completed_date', 'status', 'technician']
    list_filter = ['status', 'completed', 'scheduled_date']
    search_fields = [
        'maintenance_plan__device__name',
        'maintenance_plan__virtual_machine__name',
        'maintenance_plan__name',
        'technician',
    ]
    ordering = ['-scheduled_date']
