"""Regression coverage for historical cycle starts and calendar scheduling (#26)."""

from datetime import date, datetime, timedelta, timezone as dt_timezone
from io import StringIO
from unittest.mock import patch
from uuid import uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Job
from extras.choices import EventRuleActionChoices
from extras.models import Notification

from netbox_maintenance_device.forms import MaintenancePlanForm
from netbox_maintenance_device.jobs import CheckMaintenanceJob
from netbox_maintenance_device.models import MaintenanceExecution, MaintenancePlan
from netbox_maintenance_device.tests import test_compatibility as compatibility

NOW = datetime(2026, 10, 15, 12, tzinfo=dt_timezone.utc)


class SchedulingTestCase(TestCase):
    create_rule = compatibility.CompatibilityTestCase.create_rule
    notification_group = compatibility.CompatibilityTestCase.notification_group

    @classmethod
    def setUpTestData(cls):
        compatibility.CompatibilityTestCase.setUpTestData.__func__(cls)
        MaintenancePlan.objects.all().delete()

    def setUp(self):
        clock = patch("django.utils.timezone.now", return_value=NOW)
        clock.start()
        self.addCleanup(clock.stop)
        zone = timezone.override("UTC")
        zone.__enter__()
        self.addCleanup(zone.__exit__, None, None, None)
        self.client.force_login(self.user)
        self.api = APIClient()
        self.api.force_authenticate(self.user)

    def make_plan(self, **kwargs):
        data = dict(device=self.device, name=str(uuid4()), frequency_days=3, frequency_unit="years")
        data.update(kwargs)
        return MaintenancePlan.objects.create(**data)

    def api_url(self, model="maintenanceplan", pk=None, action=None):
        suffix = action or ("detail" if pk else "list")
        return reverse(
            f"plugins-api:netbox_maintenance_device-api:{model}-{suffix}",
            kwargs={"pk": pk} if pk else None,
        )

    def complete_at(self, plan, when):
        return MaintenanceExecution.objects.create(
            maintenance_plan=plan,
            scheduled_date=when,
            completed_date=when,
            status="completed",
        )

    def test_start_date_accounts_for_existing_battery_age(self):
        plan = self.make_plan(start_date=date(2025, 10, 15))
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2028, 10, 15))
        self.assertEqual(plan.created, NOW)

    def test_historical_start_keeps_missed_cycle_overdue(self):
        for anchor in (None, date(2022, 10, 15)):
            with self.subTest(anchor=anchor):
                plan = self.make_plan(start_date=date(2022, 10, 15), anchor_date=anchor)
                self.assertEqual(plan.get_next_maintenance_date().date(), date(2025, 10, 15))
                self.assertTrue(plan.is_overdue())
                self.assertLess(plan.days_until_due(), 0)

    def test_no_start_date_preserves_creation_reference(self):
        plan = self.make_plan()
        self.assertIsNone(plan.start_date)
        self.assertEqual(plan.get_next_maintenance_date(), NOW.replace(year=2029))

    def test_legacy_anchor_without_start_keeps_original_phase(self):
        plan = self.make_plan(anchor_date=date(2022, 10, 15))
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2028, 10, 15))

    def test_last_dated_completion_takes_precedence_over_start(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        self.complete_at(plan, NOW.replace(year=2025, month=11))
        self.complete_at(plan, NOW.replace(year=2024))
        self.assertEqual(plan.get_next_maintenance_date(), NOW.replace(year=2028, month=11))

    def test_undated_legacy_completion_does_not_hide_valid_reference(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        MaintenanceExecution.objects.create(
            maintenance_plan=plan,
            scheduled_date=NOW,
            status="completed",
        )
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2025, 10, 15))
        self.complete_at(plan, NOW.replace(year=2025))
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2028, 10, 15))

    def test_pending_and_cancelled_executions_do_not_reset_cycle(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        for status in ("scheduled", "in_progress", "cancelled"):
            MaintenanceExecution.objects.create(
                maintenance_plan=plan,
                scheduled_date=NOW,
                status=status,
            )
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2025, 10, 15))

    def test_all_interval_units_use_start_date(self):
        for unit, expected in (
            ("days", date(2026, 1, 3)),
            ("weeks", date(2026, 1, 15)),
            ("months", date(2026, 3, 1)),
            ("quarters", date(2026, 7, 1)),
            ("years", date(2028, 1, 1)),
        ):
            with self.subTest(unit=unit):
                plan = self.make_plan(
                    start_date=date(2026, 1, 1), frequency_days=2, frequency_unit=unit
                )
                self.assertEqual(plan.get_next_maintenance_date().date(), expected)

    def test_future_cycle_start_is_supported(self):
        plan = self.make_plan(start_date=date(2027, 10, 15))
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2030, 10, 15))

    def test_anchor_preserves_phase_after_late_completion(self):
        plan = self.make_plan(start_date=date(2022, 10, 15), anchor_date=date(2022, 10, 15))
        self.complete_at(plan, NOW.replace(year=2025, month=11))
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2028, 10, 15))

    def test_month_end_and_leap_day_anchor_recover_original_day(self):
        cases = (
            ("months", 1, date(2026, 1, 31), date(2026, 3, 1), date(2026, 3, 31)),
            ("months", 2, date(2026, 1, 31), date(2026, 4, 1), date(2026, 5, 31)),
            ("quarters", 1, date(2026, 1, 31), date(2026, 5, 1), date(2026, 7, 31)),
            ("years", 1, date(2024, 2, 29), date(2027, 10, 15), date(2028, 2, 29)),
        )
        for unit, count, anchor, start, expected in cases:
            with self.subTest(unit=unit, count=count):
                plan = self.make_plan(
                    frequency_unit=unit, frequency_days=count, anchor_date=anchor, start_date=start
                )
                self.assertEqual(plan.get_next_maintenance_date().date(), expected)

    def test_anchor_handles_more_than_ten_thousand_occurrences(self):
        plan = self.make_plan(anchor_date=date(1990, 1, 1), frequency_days=1, frequency_unit="days")
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2026, 10, 16))

    def test_anchor_future_and_exact_reference_boundaries(self):
        for start, anchor, expected in (
            (date(2026, 1, 1), date(2027, 1, 1), date(2027, 1, 1)),
            (date(2026, 1, 1), date(2026, 1, 1), date(2029, 1, 1)),
        ):
            with self.subTest(anchor=anchor):
                plan = self.make_plan(start_date=start, anchor_date=anchor)
                self.assertEqual(plan.get_next_maintenance_date().date(), expected)

    def test_calendar_units_keep_quarter_week_and_day_phase(self):
        cases = (
            ("days", 10, date(2026, 10, 1), date(2026, 10, 21)),
            ("weeks", 2, date(2026, 10, 1), date(2026, 10, 29)),
            ("months", 3, date(2026, 1, 1), date(2027, 1, 1)),
            ("quarters", 1, date(2026, 1, 1), date(2027, 1, 1)),
        )
        for unit, count, anchor, expected in cases:
            with self.subTest(unit=unit):
                plan = self.make_plan(frequency_unit=unit, frequency_days=count, anchor_date=anchor)
                self.assertEqual(plan.get_next_maintenance_date().date(), expected)

    def test_anchor_uses_local_calendar_when_utc_date_differs(self):
        plan = self.make_plan(anchor_date=date(1990, 1, 1), frequency_days=1, frequency_unit="days")
        MaintenancePlan.objects.filter(pk=plan.pk).update(created=NOW.replace(hour=2))
        plan.refresh_from_db()
        with timezone.override("America/Sao_Paulo"):
            due = plan.get_next_maintenance_date()
            self.assertEqual(due.date(), date(2026, 10, 15))
            self.assertEqual(due.utcoffset(), timedelta(hours=-3))

    def test_daily_anchor_stays_at_local_midnight_across_dst(self):
        plan = self.make_plan(anchor_date=date(2026, 3, 7), frequency_days=1, frequency_unit="days")
        MaintenancePlan.objects.filter(pk=plan.pk).update(created=NOW.replace(month=3, day=8))
        plan.refresh_from_db()
        with timezone.override("America/New_York"):
            due = plan.get_next_maintenance_date()
            self.assertEqual(due.date(), date(2026, 3, 9))
            self.assertEqual(due.hour, 0)
            self.assertEqual(due.utcoffset(), timedelta(hours=-4))

    def test_form_accepts_start_for_devices_and_vms(self):
        for field, target in (("device", self.device), ("virtual_machine", self.vm)):
            with self.subTest(field=field):
                form = MaintenancePlanForm(
                    data={
                        field: target.pk,
                        "name": str(uuid4()),
                        "frequency_days": 3,
                        "frequency_unit": "years",
                        "maintenance_type": "preventive",
                        "start_date": "2022-10-15",
                        "is_active": True,
                    }
                )
                self.assertTrue(form.is_valid(), form.errors.as_json())
                plan = form.save()
                self.assertEqual(plan.start_date, date(2022, 10, 15))
                self.assertTrue(plan.is_overdue())

    def test_form_rejects_invalid_start_and_localized_edit_keeps_iso_date(self):
        form = MaintenancePlanForm(data={"start_date": "2026-02-30"})
        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)
        plan = self.make_plan(start_date=date(2022, 10, 15), anchor_date=date(2022, 10, 15))
        with timezone.override("America/Sao_Paulo"):
            from django.utils.translation import override

            with override("pt-br"):
                form = MaintenancePlanForm(instance=plan)
                self.assertIn('value="2022-10-15"', str(form["start_date"]))
                self.assertIn('value="2022-10-15"', str(form["anchor_date"]))
                self.assertEqual(
                    str(form.fields["start_date"].label), "Data de início do ciclo (opcional)"
                )

    def test_ui_create_and_edit_start_without_changing_creation_timestamp(self):
        data = {
            "device": self.device.pk,
            "name": "UI battery cycle",
            "frequency_days": 3,
            "frequency_unit": "years",
            "maintenance_type": "preventive",
            "start_date": "2025-10-15",
            "is_active": True,
        }
        response = self.client.post(
            reverse("plugins:netbox_maintenance_device:maintenanceplan_add"), data
        )
        self.assertEqual(response.status_code, 302)
        plan = MaintenancePlan.objects.get(name=data["name"])
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2028, 10, 15))
        data["start_date"] = "2022-10-15"
        response = self.client.post(
            reverse("plugins:netbox_maintenance_device:maintenanceplan_edit", args=[plan.pk]), data
        )
        self.assertEqual(response.status_code, 302)
        plan.refresh_from_db()
        self.assertEqual(plan.created, NOW)
        self.assertTrue(plan.is_overdue())

    def test_api_create_edit_clear_start_for_devices_and_vms(self):
        for field, target in (("device", self.device), ("virtual_machine", self.vm)):
            with self.subTest(field=field):
                response = self.api.post(
                    self.api_url(),
                    {
                        field: target.pk,
                        "name": str(uuid4()),
                        "frequency_days": 3,
                        "frequency_unit": "years",
                        "start_date": "2025-10-15",
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 201, response.data)
                pk = response.data["id"]
                self.assertEqual(response.data["start_date"], "2025-10-15")
                self.assertEqual(str(response.data["next_maintenance_date"])[:10], "2028-10-15")
                response = self.api.patch(
                    self.api_url(pk=pk), {"start_date": "2022-10-15"}, format="json"
                )
                self.assertEqual(response.status_code, 200, response.data)
                self.assertTrue(response.data["is_overdue"])
                response = self.api.patch(self.api_url(pk=pk), {"start_date": None}, format="json")
                self.assertEqual(response.status_code, 200, response.data)
                self.assertIsNone(response.data["start_date"])
                self.assertEqual(str(response.data["next_maintenance_date"])[:10], "2029-10-15")

    def test_api_rejects_invalid_start_date(self):
        plan = self.make_plan()
        response = self.api.patch(
            self.api_url(pk=plan.pk), {"start_date": "2026-02-30"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("start_date", response.data)

    def test_overdue_start_reaches_dashboard_api_and_details(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        response = self.client.get(
            reverse("plugins:netbox_maintenance_device:upcoming_maintenance"), {"status": "overdue"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overdue_count"], 1)
        self.assertEqual(response.context["on_track_count"], 0)
        response = self.api.get(self.api_url(action="overdue"))
        self.assertEqual(response.status_code, 200, response.data)
        rows = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertEqual([row["id"] for row in rows], [plan.pk])
        response = self.client.get(plan.get_absolute_url())
        self.assertContains(response, "2022-10-15")
        self.assertContains(response, "2025-10-15")

    def test_command_notifies_historical_cycle_once(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        self.create_rule(
            MaintenancePlan,
            ["maintenance_due"],
            self.notification_group(),
            EventRuleActionChoices.NOTIFICATION,
        )
        from django.core.management import call_command

        for _ in range(2):
            call_command("check_maintenance", stdout=StringIO())
        plan.refresh_from_db()
        self.assertEqual(plan.last_notified_date, date(2025, 10, 15))
        self.assertEqual(Notification.objects.filter(event_type="maintenance_due").count(), 1)

    def test_daily_job_notifies_historical_cycle_once(self):
        plan = self.make_plan(start_date=date(2022, 10, 15))
        self.create_rule(
            MaintenancePlan,
            ["maintenance_due"],
            self.notification_group(),
            EventRuleActionChoices.NOTIFICATION,
        )
        job = Job.objects.create(name="Historical cycle test", job_id=uuid4())
        runner = CheckMaintenanceJob(job)
        self.addCleanup(runner.logger.removeHandler, runner.logger.handlers[-1])
        runner.run()
        runner.run()
        plan.refresh_from_db()
        self.assertEqual(plan.last_notified_date, date(2025, 10, 15))
        self.assertEqual(Notification.objects.filter(event_type="maintenance_due").count(), 1)

    def test_api_imports_and_partially_updates_old_completed_history(self):
        plan = self.make_plan()
        when = NOW.replace(year=2022).isoformat()
        response = self.api.post(
            self.api_url("maintenanceexecution"),
            {
                "maintenance_plan": plan.pk,
                "scheduled_date": when,
                "completed_date": when,
                "status": "completed",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2025, 10, 15))
        execution_url = self.api_url("maintenanceexecution", pk=response.data["id"])
        response = self.api.patch(execution_url, {"notes": "Imported installation"}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        response = self.api.patch(
            execution_url, {"completed_date": NOW.replace(year=2023).isoformat()}, format="json"
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(plan.get_next_maintenance_date().date(), date(2026, 10, 15))

    def test_api_keeps_pending_history_limit_at_365_days(self):
        plan = self.make_plan()
        for age, expected in ((365, 201), (366, 400)):
            with self.subTest(age=age):
                response = self.api.post(
                    self.api_url("maintenanceexecution"),
                    {
                        "maintenance_plan": plan.pk,
                        "scheduled_date": (NOW - timedelta(days=age)).isoformat(),
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, expected, response.data)
                if expected == 400:
                    self.assertIn("scheduled_date", response.data)

    def test_api_rejects_inconsistent_historical_completion(self):
        plan = self.make_plan()
        when = NOW.replace(year=2022).isoformat()
        for invalid in (
            {"completed_date": None},
            {"completed_date": NOW.replace(year=2021).isoformat()},
            {"completed_date": (NOW + timedelta(days=1)).isoformat()},
            {"status": "scheduled"},
        ):
            with self.subTest(invalid=invalid):
                response = self.api.post(
                    self.api_url("maintenanceexecution"),
                    {
                        "maintenance_plan": plan.pk,
                        "scheduled_date": when,
                        "completed_date": when,
                        "status": "completed",
                        **invalid,
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(plan.executions.count(), 0)

    def test_api_partial_updates_validate_against_persisted_dates(self):
        plan = self.make_plan()
        execution = self.complete_at(plan, NOW.replace(year=2022))
        url = self.api_url("maintenanceexecution", pk=execution.pk)
        for data in (
            {"completed_date": NOW.replace(year=2021).isoformat()},
            {"scheduled_date": NOW.replace(year=2023).isoformat()},
            {"status": "scheduled", "completed_date": None},
        ):
            with self.subTest(data=data):
                response = self.api.patch(url, data, format="json")
                self.assertEqual(response.status_code, 400, response.data)
        execution.refresh_from_db()
        self.assertEqual(execution.status, "completed")
        self.assertEqual(execution.completed_date, NOW.replace(year=2022))

    def test_api_can_edit_notes_on_legacy_old_pending_schedule(self):
        plan = self.make_plan()
        execution = MaintenanceExecution.objects.create(
            maintenance_plan=plan, scheduled_date=NOW.replace(year=2022), status="scheduled"
        )
        response = self.api.patch(
            self.api_url("maintenanceexecution", pk=execution.pk),
            {"notes": "Legacy schedule retained"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)


class StartDateMigrationTestCase(TransactionTestCase):
    def test_existing_plans_and_execution_history_survive_additive_migration(self):
        previous = (
            "netbox_maintenance_device",
            "0004_remove_maintenanceplan_last_executed_and_more",
        )
        latest = ("netbox_maintenance_device", "0005_maintenanceplan_start_date")
        executor = MigrationExecutor(connection)
        executor.migrate([previous])
        try:
            targets = [
                node
                for node in executor.loader.graph.leaf_nodes()
                if node[0] != "netbox_maintenance_device"
            ] + [previous]
            old_apps = executor.loader.project_state(targets).apps
            vm = old_apps.get_model("virtualization", "VirtualMachine").objects.create(
                name="Legacy VM"
            )
            old_plan = old_apps.get_model("netbox_maintenance_device", "MaintenancePlan")
            plan = old_plan.objects.create(
                virtual_machine_id=vm.pk,
                name="Legacy cycle",
                frequency_days=1,
                frequency_unit="quarters",
                anchor_date=date(2026, 1, 1),
                last_notified_date=date(2026, 7, 1),
                custom_field_data={"legacy": "preserved"},
            )
            old_execution = old_apps.get_model("netbox_maintenance_device", "MaintenanceExecution")
            execution = old_execution.objects.create(
                maintenance_plan_id=plan.pk,
                scheduled_date=NOW.replace(month=7, day=1),
                completed_date=NOW.replace(month=7, day=2),
                status="completed",
                completed=True,
                notes="Preserve existing history",
                technician="Operator",
            )
            plan_before = old_plan.objects.filter(pk=plan.pk).values().get()
            execution_before = old_execution.objects.filter(pk=execution.pk).values().get()
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate([latest])

        migrated = MaintenancePlan.objects.filter(pk=plan.pk).values().get()
        self.assertIsNone(migrated.pop("start_date"))
        self.assertEqual(migrated, plan_before)
        self.assertEqual(
            MaintenanceExecution.objects.filter(pk=execution.pk).values().get(), execution_before
        )
