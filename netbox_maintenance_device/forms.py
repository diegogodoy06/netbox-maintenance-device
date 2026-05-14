import django_filters
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.filtersets import NetBoxModelFilterSet
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from virtualization.models import VirtualMachine

from . import models


class MaintenancePlanForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        selector=True,
        label=_('Device'),
        help_text=_("Pick a device — or pick a virtual machine below, not both."),
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        selector=True,
        label=_('Virtual Machine'),
        help_text=_("Pick a virtual machine — or pick a device above, not both."),
    )

    class Meta:
        model = models.MaintenancePlan
        fields = [
            'device', 'virtual_machine', 'name', 'description', 'maintenance_type',
            'frequency_days', 'frequency_unit', 'anchor_date', 'is_active', 'tags',
        ]
        widgets = {
            'anchor_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        vm = cleaned_data.get('virtual_machine')
        if device and vm:
            raise ValidationError(_(
                "Pick either a device or a virtual machine, not both."
            ))
        if not device and not vm:
            raise ValidationError(_(
                "Pick a device or a virtual machine for this plan."
            ))
        return cleaned_data


class MaintenancePlanFilterSet(NetBoxModelFilterSet):
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        field_name='device',
    )
    virtual_machine = django_filters.ModelChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        field_name='virtual_machine',
    )
    maintenance_type = django_filters.ChoiceFilter(
        choices=models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES
    )
    frequency_unit = django_filters.ChoiceFilter(
        choices=models.MaintenancePlan.FREQUENCY_UNIT_CHOICES
    )

    class Meta:
        model = models.MaintenancePlan
        fields = ['device', 'virtual_machine', 'maintenance_type', 'frequency_unit', 'is_active']


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
