import django_filters
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.filtersets import NetBoxModelFilterSet
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine

from . import models


class MaintenancePlanForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        selector=True,
        label=_('Device'),
        help_text=_("Pick a device — leave Virtual Machine empty."),
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        selector=True,
        label=_('Virtual Machine'),
        help_text=_("Pick a virtual machine — leave Device empty."),
    )
    frequency_days = forms.IntegerField(
        min_value=1,
        label=_('Repeat every'),
        help_text=_("How many units between maintenances (e.g. '1' + 'Months' = monthly)."),
    )
    frequency_unit = forms.ChoiceField(
        choices=models.MaintenancePlan.FREQUENCY_UNIT_CHOICES,
        label=_('Unit'),
        help_text=_("Days / weeks / months / quarters / years."),
    )
    anchor_date = forms.DateField(
        required=False,
        label=_('Calendar anchor (optional)'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text=_(
            "Use this to lock the schedule to a calendar date and avoid drift. "
            "Examples: pick any 1st-of-month to schedule on the 1st of every month; "
            "pick 2026-01-01 with unit 'quarters' to land on Jan 1 / Apr 1 / Jul 1 / Oct 1. "
            "Leave blank for a simple rolling interval from the last completion."
        ),
    )

    fieldsets = (
        FieldSet('name', 'description', 'maintenance_type', 'is_active', name=_('Plan')),
        FieldSet('device', 'virtual_machine', name=_('Target')),
        FieldSet('frequency_days', 'frequency_unit', 'anchor_date', name=_('Schedule')),
        FieldSet('tags', name=_('Tags')),
    )

    class Meta:
        model = models.MaintenancePlan
        fields = [
            'device', 'virtual_machine', 'name', 'description', 'maintenance_type',
            'frequency_days', 'frequency_unit', 'anchor_date', 'is_active', 'tags',
        ]

    class Media:
        # Disables the other target field when one is selected.
        js = ('netbox_maintenance_device/js/plan_target_toggle.js',)

    def clean(self):
        # NetBoxModelForm.clean() modifies self.cleaned_data in place but may not
        # return it (Django allows either pattern), so we read from self.cleaned_data
        # directly to avoid a NoneType crash.
        super().clean()
        cleaned_data = self.cleaned_data or {}
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
