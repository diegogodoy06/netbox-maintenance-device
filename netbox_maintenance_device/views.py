from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from netbox.views import generic
from dcim.models import Device
from . import forms, models, tables


class MaintenancePlanListView(generic.ObjectListView):
    queryset = models.MaintenancePlan.objects.all()
    table = tables.MaintenancePlanTable
    filterset = forms.MaintenancePlanFilterSet


class MaintenancePlanView(generic.ObjectView):
    queryset = models.MaintenancePlan.objects.all()


class MaintenancePlanEditView(generic.ObjectEditView):
    queryset = models.MaintenancePlan.objects.all()
    form = forms.MaintenancePlanForm


class MaintenancePlanDeleteView(generic.ObjectDeleteView):
    queryset = models.MaintenancePlan.objects.all()


class MaintenancePlanChangeLogView(generic.ObjectChangeLogView):
    queryset = models.MaintenancePlan.objects.all()
    
    def get_extra_context(self, request, instance):
        return {
            'model': models.MaintenancePlan,
        }


class MaintenanceExecutionListView(generic.ObjectListView):
    queryset = models.MaintenanceExecution.objects.all()
    table = tables.MaintenanceExecutionTable
    filterset = forms.MaintenanceExecutionFilterSet


class MaintenanceExecutionView(generic.ObjectView):
    queryset = models.MaintenanceExecution.objects.all()


class MaintenanceExecutionEditView(generic.ObjectEditView):
    queryset = models.MaintenanceExecution.objects.all()
    form = forms.MaintenanceExecutionForm


class MaintenanceExecutionDeleteView(generic.ObjectDeleteView):
    queryset = models.MaintenanceExecution.objects.all()


class MaintenanceExecutionChangeLogView(generic.ObjectChangeLogView):
    queryset = models.MaintenanceExecution.objects.all()
    
    def get_extra_context(self, request, instance):
        return {
            'model': models.MaintenanceExecution,
        }


class UpcomingMaintenanceView(generic.ObjectListView):
    """View for upcoming and overdue maintenance"""
    queryset = models.MaintenancePlan.objects.filter(is_active=True)
    table = tables.UpcomingMaintenanceTable
    template_name = 'netbox_maintenance_device/upcoming_maintenance.html'
    
    def get_queryset(self, request):
        # Get all active maintenance plans
        queryset = super().get_queryset(request)
        
        # For now, show all active plans
        # TODO: Implement proper upcoming logic
        return queryset


def device_maintenance_tab(request, pk):
    """Tab view for device maintenance history"""
    device = get_object_or_404(Device, pk=pk)
    maintenance_plans = models.MaintenancePlan.objects.filter(device=device)
    recent_executions = models.MaintenanceExecution.objects.filter(
        maintenance_plan__device=device
    ).order_by('-scheduled_date')[:10]
    
    context = {
        'device': device,
        'maintenance_plans': maintenance_plans,
        'recent_executions': recent_executions,
    }
    
    return render(request, 'netbox_maintenance_device/device_maintenance_tab.html', context)