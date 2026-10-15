from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_maintenance_device", "0004_remove_maintenanceplan_last_executed_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenanceplan",
            name="start_date",
            field=models.DateField(
                blank=True,
                null=True,
                help_text=(
                    "Installation date or start of the maintenance cycle, used until "
                    "the first completed maintenance. Leave blank to use the plan creation date."
                ),
                verbose_name="Cycle Start Date",
            ),
        ),
    ]
