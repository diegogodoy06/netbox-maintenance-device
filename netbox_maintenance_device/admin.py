from django.contrib import admin
from . import models

@admin.register(models.MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ['device', 'name', 'maintenance_type', 'frequency_days', 'is_active', 'created']
    list_filter = ['maintenance_type', 'is_active', 'created']
    search_fields = ['device__name', 'name', 'description']
    ordering = ['device', 'name']

@admin.register(models.MaintenanceExecution)
class MaintenanceExecutionAdmin(admin.ModelAdmin):
    list_display = ['maintenance_plan', 'scheduled_date', 'completed_date', 'status', 'technician']
    list_filter = ['status', 'completed', 'scheduled_date']
    search_fields = ['maintenance_plan__device__name', 'maintenance_plan__name', 'technician']
    ordering = ['-scheduled_date']