"""Seed and compare persistent data around a real NetBox database upgrade."""

from datetime import date, datetime, timezone

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.models import Tag
from virtualization.models import VirtualMachine

from netbox_maintenance_device.models import MaintenanceExecution, MaintenancePlan


def seed_upgrade_data():
    site = Site.objects.create(name="Upgrade site", slug="upgrade-site")
    manufacturer = Manufacturer.objects.create(name="Upgrade vendor", slug="upgrade-vendor")
    device_type = DeviceType.objects.create(
        manufacturer=manufacturer, model="Upgrade model", slug="upgrade-model"
    )
    role = DeviceRole.objects.create(name="Upgrade role", slug="upgrade-role")
    device = Device.objects.create(
        name="Upgrade device", site=site, device_type=device_type, role=role
    )
    vm = VirtualMachine.objects.create(name="Upgrade VM")
    tag = Tag.objects.create(name="Upgrade tag", slug="upgrade-tag")
    for target in ({"device": device}, {"virtual_machine": vm}):
        plan = MaintenancePlan.objects.create(
            **target,
            name="Upgrade plan",
            frequency_days=1,
            frequency_unit="quarters",
            start_date=date(2025, 10, 1),
            anchor_date=date(2026, 1, 1),
            last_notified_date=date(2026, 7, 1),
        )
        plan.tags.add(tag)
        MaintenanceExecution.objects.create(
            maintenance_plan=plan,
            scheduled_date=datetime(2026, 7, 1, tzinfo=timezone.utc),
            completed_date=datetime(2026, 7, 2, tzinfo=timezone.utc),
            status="completed",
            notes="Preserve this execution",
            technician="Upgrade operator",
        )


def upgrade_snapshot():
    """Compare IDs, relationships, scheduling state, tags and execution history."""
    result = []
    for plan in MaintenancePlan.objects.filter(name="Upgrade plan").order_by("pk"):
        result.append(
            {
                "id": plan.pk,
                "target_id": plan.target.pk,
                "target_name": plan.target_name,
                "target_type": plan.target_type,
                "frequency_days": plan.frequency_days,
                "frequency_unit": plan.frequency_unit,
                "start_date": plan.start_date.isoformat() if plan.start_date else None,
                "anchor_date": plan.anchor_date.isoformat(),
                "last_notified_date": plan.last_notified_date.isoformat(),
                "next_due": plan.get_next_maintenance_date().isoformat(),
                "tags": list(plan.tags.order_by("pk").values_list("pk", "name")),
                "executions": list(
                    plan.executions.values(
                        "id",
                        "maintenance_plan_id",
                        "scheduled_date",
                        "completed_date",
                        "status",
                        "completed",
                        "notes",
                        "technician",
                    )
                ),
            }
        )
    assert len(result) == 2, "Both the device and VM maintenance plans must survive the upgrade"
    return result
