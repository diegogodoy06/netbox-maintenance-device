# Generated migration for MaintenanceNotification model

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_maintenance_device', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MaintenanceNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('notification_type', models.CharField(choices=[('overdue', 'Overdue'), ('due_soon', 'Due Soon'), ('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], max_length=20, verbose_name='Type')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10, verbose_name='Priority')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('message', models.TextField(verbose_name='Message')),
                ('is_read', models.BooleanField(default=False, verbose_name='Read')),
                ('is_sent_browser', models.BooleanField(default=False, verbose_name='Sent to Browser')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Read At')),
                ('maintenance_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='netbox_maintenance_device.maintenanceplan', verbose_name='Maintenance Plan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_notifications', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Maintenance Notification',
                'verbose_name_plural': 'Maintenance Notifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
