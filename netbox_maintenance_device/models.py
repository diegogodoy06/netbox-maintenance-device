from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dcim.models import Device
from netbox.models import NetBoxModel
from virtualization.models import VirtualMachine


# Max iterations when stepping forward from an anchor_date to the next due date.
# Bounds the loop so a degenerate (zero-width) step can never spin forever.
_ANCHOR_STEP_MAX_ITERATIONS = 10000


class MaintenancePlan(NetBoxModel):
    """Maintenance plan for a device or a virtual machine.

    A plan targets exactly one of `device` or `virtual_machine`. Scheduling is
    expressed as a (`frequency_days`, `frequency_unit`) pair, optionally
    anchored to `anchor_date` to avoid calendar drift (e.g. "start of each
    quarter").
    """

    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', _('Preventive')),
        ('corrective', _('Corrective')),
    ]

    FREQUENCY_UNIT_CHOICES = [
        ('days', _('Days')),
        ('weeks', _('Weeks')),
        ('months', _('Months')),
        ('quarters', _('Quarters')),
        ('years', _('Years')),
    ]

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='maintenance_plans',
        null=True,
        blank=True,
        verbose_name=_('Device'),
    )
    virtual_machine = models.ForeignKey(
        VirtualMachine,
        on_delete=models.CASCADE,
        related_name='maintenance_plans',
        null=True,
        blank=True,
        verbose_name=_('Virtual Machine'),
    )
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES,
        default='preventive',
        verbose_name=_('Maintenance Type'),
    )
    frequency_days = models.PositiveIntegerField(
        help_text=_("Number of frequency units between maintenances"),
        verbose_name=_('Frequency'),
    )
    frequency_unit = models.CharField(
        max_length=20,
        choices=FREQUENCY_UNIT_CHOICES,
        default='days',
        verbose_name=_('Frequency Unit'),
    )
    anchor_date = models.DateField(
        null=True,
        blank=True,
        help_text=_(
            "Optional anchor date. When set, future maintenances are computed "
            "from this date instead of from the last execution, preventing "
            "calendar drift (useful for 'start of each quarter' schedules)."
        ),
        verbose_name=_('Anchor Date'),
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    last_notified_date = models.DateField(
        null=True,
        blank=True,
        help_text=_(
            "The last due date for which a notification was sent, to avoid "
            "duplicate alerts."
        ),
        verbose_name=_('Last Notified Date'),
    )

    class Meta:
        ordering = ['device', 'virtual_machine', 'name']
        verbose_name = _('Maintenance Plan')
        verbose_name_plural = _('Maintenance Plans')
        constraints = [
            models.UniqueConstraint(
                fields=['device', 'name'],
                condition=models.Q(device__isnull=False),
                name='unique_device_plan_name',
            ),
            models.UniqueConstraint(
                fields=['virtual_machine', 'name'],
                condition=models.Q(virtual_machine__isnull=False),
                name='unique_vm_plan_name',
            ),
        ]

    @property
    def target(self):
        """Return the assigned Device or VirtualMachine (whichever is set)."""
        return self.device or self.virtual_machine

    @property
    def target_type(self):
        """Return 'device', 'virtualmachine', or None."""
        if self.device_id:
            return 'device'
        if self.virtual_machine_id:
            return 'virtualmachine'
        return None

    @property
    def target_name(self):
        target = self.target
        return target.name if target else ''

    def clean(self):
        super().clean()
        has_device = self.device_id is not None
        has_vm = self.virtual_machine_id is not None
        if has_device and has_vm:
            raise ValidationError(_(
                "A maintenance plan cannot reference both a device and a "
                "virtual machine; pick one."
            ))
        if not has_device and not has_vm:
            raise ValidationError(_(
                "A maintenance plan must reference either a device or a "
                "virtual machine."
            ))

    def __str__(self):
        return f"{self.target_name or _('(no target)')} - {self.name}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenance_device:maintenanceplan', args=[self.pk])

    def get_frequency_display(self):
        """Human-readable frequency string, e.g. '30 days' or 'Every 2 quarters'."""
        count = self.frequency_days or 1
        unit_label = dict(self.FREQUENCY_UNIT_CHOICES).get(self.frequency_unit, self.frequency_unit)
        return f"{count} {unit_label}"

    def _step_delta(self):
        """Return a relativedelta representing one step between maintenances."""
        count = self.frequency_days or 1
        unit = self.frequency_unit or 'days'
        if unit == 'weeks':
            return relativedelta(weeks=count)
        if unit == 'months':
            return relativedelta(months=count)
        if unit == 'quarters':
            return relativedelta(months=count * 3)
        if unit == 'years':
            return relativedelta(years=count)
        return relativedelta(days=count)

    def get_next_maintenance_date(self):
        """Compute the next scheduled maintenance date.

        Two modes:

        - Anchor mode (`anchor_date` is set): returns the smallest
          `anchor_date + n * step` (n >= 0) that is strictly greater than the
          reference date. This avoids drift over time, so a quarterly schedule
          anchored on Jan 1 stays on Jan 1 / Apr 1 / Jul 1 / Oct 1 regardless
          of when previous executions actually happened.
        - Interval mode (no anchor): returns reference + step.

        Reference date is the last completed execution's `completed_date`, or
        the plan's `created` timestamp if there are no completed executions.
        """
        last_execution = self.executions.filter(
            completed=True
        ).order_by('-completed_date').first()
        reference = last_execution.completed_date if last_execution else self.created
        if reference is None:
            reference = timezone.now()

        step = self._step_delta()

        if self.anchor_date:
            anchor_dt = timezone.make_aware(
                datetime.combine(self.anchor_date, time.min)
            )
            if anchor_dt > reference:
                return anchor_dt
            candidate = anchor_dt
            for _i in range(_ANCHOR_STEP_MAX_ITERATIONS):
                candidate = candidate + step
                if candidate > reference:
                    return candidate
            return candidate

        return reference + step

    def is_overdue(self):
        next_date = self.get_next_maintenance_date()
        return timezone.now().date() > next_date.date() if next_date else False

    def days_until_due(self):
        next_date = self.get_next_maintenance_date()
        if next_date:
            delta = next_date.date() - timezone.now().date()
            return delta.days
        return None


class MaintenanceExecution(NetBoxModel):
    """Record of maintenance execution"""

    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    maintenance_plan = models.ForeignKey(
        MaintenancePlan,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('Plan')
    )
    scheduled_date = models.DateTimeField(verbose_name=_('Scheduled Date'))
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed Date'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name=_('Status')
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    technician = models.CharField(max_length=100, blank=True, verbose_name=_('Technician'))
    completed = models.BooleanField(default=False, verbose_name=_('Completed'))

    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = _('Maintenance Execution')
        verbose_name_plural = _('Maintenance Executions')

    def __str__(self):
        return f"{self.maintenance_plan} - {self.scheduled_date.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenance_device:maintenanceexecution', args=[self.pk])

    def save(self, *args, **kwargs):
        # Auto-set completed flag based on status
        self.completed = self.status == 'completed'
        
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_status = MaintenanceExecution.objects.only('status').get(pk=self.pk).status
            except MaintenanceExecution.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)
        
        # Fire events
        from .events import fire_event
        if is_new:
            if self.status == 'scheduled':
                fire_event(self, 'maintenance_scheduled')
            elif self.status == 'completed':
                fire_event(self, 'maintenance_completed')
        else:
            if self.status == 'scheduled' and old_status != 'scheduled':
                fire_event(self, 'maintenance_scheduled')
            elif self.status == 'completed' and old_status != 'completed':
                fire_event(self, 'maintenance_completed')
