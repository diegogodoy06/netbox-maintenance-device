from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from dcim.models import Device
from utilities.forms.fields import DynamicModelChoiceField
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


class MaintenancePlanFilterSet(NetBoxModelFilterSetForm):
    model = models.MaintenancePlan
    
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    maintenance_type = forms.ChoiceField(
        choices=[('', 'All')] + models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES,
        required=False
    )
    is_active = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', 'All'),
            ('true', 'Active'),
            ('false', 'Inactive')
        ])
    )


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


class MaintenanceExecutionFilterSet(NetBoxModelFilterSetForm):
    model = models.MaintenanceExecution
    
    maintenance_plan = DynamicModelChoiceField(
        queryset=models.MaintenancePlan.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + models.MaintenanceExecution.STATUS_CHOICES,
        required=False
    )
    completed = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', 'All'),
            ('true', 'Completed'),
            ('false', 'Not Completed')
        ])
    )