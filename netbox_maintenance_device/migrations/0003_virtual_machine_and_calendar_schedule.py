"""Add VirtualMachine support and calendar-based scheduling.

This migration:

- Makes ``MaintenancePlan.device`` nullable.
- Adds ``MaintenancePlan.virtual_machine`` (FK to ``virtualization.VirtualMachine``).
- Adds ``MaintenancePlan.frequency_unit`` (days/weeks/months/quarters/years).
- Adds ``MaintenancePlan.anchor_date`` (nullable; enables drift-free schedules).
- Drops any pre-existing ``unique_together`` constraint on
  ``(device, name)`` and replaces it with two conditional ``UniqueConstraint``\
  s — one per target type — so the uniqueness rule is preserved across both
  Device and VirtualMachine targets.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_maintenance_device', '0002_cleanup_notifications'),
        ('dcim', '__latest__'),
        ('virtualization', '__latest__'),
    ]

    operations = [
        # Clear the old (device, name) unique_together so we can switch to
        # per-target conditional UniqueConstraints below. This is a no-op if
        # the database never had it applied.
        migrations.AlterUniqueTogether(
            name='maintenanceplan',
            unique_together=set(),
        ),
        # Make device nullable: a plan can now target either a device OR a VM.
        migrations.AlterField(
            model_name='maintenanceplan',
            name='device',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='maintenance_plans',
                to='dcim.device',
                verbose_name='Device',
            ),
        ),
        # Add virtual_machine FK.
        migrations.AddField(
            model_name='maintenanceplan',
            name='virtual_machine',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='maintenance_plans',
                to='virtualization.virtualmachine',
                verbose_name='Virtual Machine',
            ),
        ),
        # Add calendar-based scheduling fields.
        migrations.AddField(
            model_name='maintenanceplan',
            name='frequency_unit',
            field=models.CharField(
                choices=[
                    ('days', 'Days'),
                    ('weeks', 'Weeks'),
                    ('months', 'Months'),
                    ('quarters', 'Quarters'),
                    ('years', 'Years'),
                ],
                default='days',
                max_length=20,
                verbose_name='Frequency Unit',
            ),
        ),
        migrations.AddField(
            model_name='maintenanceplan',
            name='anchor_date',
            field=models.DateField(
                blank=True,
                help_text=(
                    "Optional anchor date. When set, future maintenances are "
                    "computed from this date instead of from the last "
                    "execution, preventing calendar drift (useful for 'start "
                    "of each quarter' schedules)."
                ),
                null=True,
                verbose_name='Anchor Date',
            ),
        ),
        migrations.AlterField(
            model_name='maintenanceplan',
            name='frequency_days',
            field=models.PositiveIntegerField(
                help_text='Number of frequency units between maintenances',
                verbose_name='Frequency',
            ),
        ),
        migrations.AlterModelOptions(
            name='maintenanceplan',
            options={
                'ordering': ['device', 'virtual_machine', 'name'],
                'verbose_name': 'Maintenance Plan',
                'verbose_name_plural': 'Maintenance Plans',
            },
        ),
        # Per-target uniqueness: plan name must be unique within each device,
        # and within each virtual machine, independently.
        migrations.AddConstraint(
            model_name='maintenanceplan',
            constraint=models.UniqueConstraint(
                condition=models.Q(('device__isnull', False)),
                fields=('device', 'name'),
                name='unique_device_plan_name',
            ),
        ),
        migrations.AddConstraint(
            model_name='maintenanceplan',
            constraint=models.UniqueConstraint(
                condition=models.Q(('virtual_machine__isnull', False)),
                fields=('virtual_machine', 'name'),
                name='unique_vm_plan_name',
            ),
        ),
    ]
