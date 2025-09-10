from django import forms
from django.utils.translation import gettext_lazy as _
from netbox.forms import NetBoxModelForm
from dcim.models import Device
from utilities.forms.fields import DynamicModelChoiceField
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from . import models


class MaintenancePlanForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        selector=True
    )
    
    class Meta:
        model = models.MaintenancePlan
        fields = [
            'device', 'name', 'description', 'maintenance_type', 
            'frequency_days', 'is_active', 'tags'
        ]


class MaintenancePlanFilterSet(NetBoxModelFilterSet):
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device'
    )
    maintenance_type = django_filters.ChoiceFilter(
        choices=models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES
    )
    
    class Meta:
        model = models.MaintenancePlan
        fields = ['device', 'maintenance_type', 'is_active']


class MaintenanceExecutionForm(NetBoxModelForm):
    maintenance_plan = DynamicModelChoiceField(
        queryset=models.MaintenancePlan.objects.all(),
        selector=True
    )
    
    class Meta:
        model = models.MaintenanceExecution
        fields = [
            'maintenance_plan', 'scheduled_date', 'completed_date',
            'status', 'notes', 'technician', 'tags'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'completed_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class MaintenanceExecutionFilterSet(NetBoxModelFilterSet):
    maintenance_plan = django_filters.ModelChoiceFilter(
        queryset=models.MaintenancePlan.objects.all(),
        field_name='maintenance_plan'
    )
    status = django_filters.ChoiceFilter(
        choices=models.MaintenanceExecution.STATUS_CHOICES
    )
    
    class Meta:
        model = models.MaintenanceExecution
        fields = ['maintenance_plan', 'status', 'completed']