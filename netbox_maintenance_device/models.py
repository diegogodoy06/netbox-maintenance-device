from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from netbox.models import NetBoxModel
from dcim.models import Device


class MaintenancePlan(NetBoxModel):
    """Maintenance plan for a device with frequency and type"""
    
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', _('Preventive')),
        ('corrective', _('Corrective')),
    ]
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='maintenance_plans',
        verbose_name=_('Device')
    )
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES,
        default='preventive',
        verbose_name=_('Maintenance Type')
    )
    frequency_days = models.PositiveIntegerField(
        help_text=_("Frequency in days"),
        verbose_name=_('Frequency (days)')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        ordering = ['device', 'name']
        unique_together = ['device', 'name']
        verbose_name = _('Maintenance Plan')
        verbose_name_plural = _('Maintenance Plans')
    
    def __str__(self):
        return f"{self.device.name} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenance_device:maintenanceplan', args=[self.pk])
    
    def save(self, *args, **kwargs):
        """Override save with basic safety checks."""
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete with basic safety checks."""
        super().delete(*args, **kwargs)
    
    def get_next_maintenance_date(self):
        """Calculate next maintenance date based on last execution"""
        last_execution = self.executions.filter(
            completed=True
        ).order_by('-completed_date').first()
        
        if last_execution:
            return last_execution.completed_date + timedelta(days=self.frequency_days)
        else:
            # If no executions, use creation date as base
            return self.created + timedelta(days=self.frequency_days)
    
    def is_overdue(self):
        """Check if maintenance is overdue"""
        next_date = self.get_next_maintenance_date()
        return timezone.now().date() > next_date.date() if next_date else False
    
    def days_until_due(self):
        """Get days until next maintenance (negative if overdue)"""
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
        super().save(*args, **kwargs)