from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from netbox.models import NetBoxModel
from dcim.models import Device
from django.contrib.auth import get_user_model
from django.conf import settings

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
    
    def create_notification(self, notification_type, priority='medium', title=None, message=None, users=None):
        """Create notifications for this maintenance plan"""
        from .models import MaintenanceNotification
        
        if not users:
            # Get staff users as default
            User = get_user_model()
            users = User.objects.filter(is_active=True, is_staff=True)
        
        notifications_created = []
        
        for user in users:
            # Check if similar notification already exists (avoid duplicates)
            existing = MaintenanceNotification.objects.filter(
                user=user,
                maintenance_plan=self,
                notification_type=notification_type,
                created_at__date=timezone.now().date()
            ).exists()
            
            if not existing:
                notification = MaintenanceNotification.objects.create(
                    user=user,
                    maintenance_plan=self,
                    notification_type=notification_type,
                    priority=priority,
                    title=title or f'{notification_type.title()} Maintenance: {self.name}',
                    message=message or f'Device {self.device.name} - {self.name}'
                )
                notifications_created.append(notification)
        
        return notifications_created


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


class MaintenanceNotification(NetBoxModel):
    """Notification for maintenance events"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('overdue', _('Overdue')),
        ('due_soon', _('Due Soon')),
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='maintenance_notifications',
        verbose_name=_('User')
    )
    maintenance_plan = models.ForeignKey(
        MaintenancePlan,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Maintenance Plan')
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name=_('Type')
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Priority')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    is_read = models.BooleanField(default=False, verbose_name=_('Read'))
    is_sent_browser = models.BooleanField(default=False, verbose_name=_('Sent to Browser'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Read At'))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Maintenance Notification')
        verbose_name_plural = _('Maintenance Notifications')
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenance_device:notification', args=[self.pk])
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def get_priority_class(self):
        """Get CSS class for priority"""
        priority_classes = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        }
        return priority_classes.get(self.priority, 'info')
    
    def get_type_icon(self):
        """Get icon for notification type"""
        type_icons = {
            'overdue': 'mdi-alert-circle',
            'due_soon': 'mdi-clock-alert',
            'scheduled': 'mdi-calendar-check',
            'completed': 'mdi-check-circle',
            'cancelled': 'mdi-cancel'
        }
        return type_icons.get(self.notification_type, 'mdi-bell')