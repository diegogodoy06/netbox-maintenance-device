"""Authentication and object permission coverage for the maintenance web views."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange, ObjectType
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from users.models import ObjectPermission

from netbox_maintenance_device.models import MaintenanceExecution, MaintenancePlan

NS = "plugins:netbox_maintenance_device:"
QUICK_COMPLETE = reverse(f"{NS}quick_complete")
SCHEDULE = reverse(f"{NS}schedule_maintenance")

recorded_events = []


def record_events(events):
    recorded_events.extend(events)


class PermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Site", slug="site")
        manufacturer = Manufacturer.objects.create(name="Manufacturer", slug="manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Type", slug="type")
        role = DeviceRole.objects.create(name="Role", slug="role")
        cls.device = Device.objects.create(name="device", site=site, device_type=device_type, role=role)

        overdue = (timezone.now() - timedelta(days=400)).date()
        cls.plan_a = MaintenancePlan.objects.create(
            device=cls.device, name="A", frequency_days=30, start_date=overdue
        )
        cls.plan_b = MaintenancePlan.objects.create(
            device=cls.device, name="B", frequency_days=30, start_date=overdue
        )
        cls.execution_a = MaintenanceExecution.objects.create(
            maintenance_plan=cls.plan_a, scheduled_date=timezone.now(), technician="tech-a"
        )
        cls.execution_b = MaintenanceExecution.objects.create(
            maintenance_plan=cls.plan_b, scheduled_date=timezone.now(), technician="tech-b"
        )

    def login(self, *grants):
        """Log in a new user holding the given (model, actions, constraints) grants."""
        user = get_user_model().objects.create_user(
            username=f"user{get_user_model().objects.count()}", first_name="Ada", last_name="Lovelace"
        )
        for index, (model, actions, constraints) in enumerate(grants):
            permission = ObjectPermission.objects.create(
                name=f"{user.username}-{index}", actions=actions, constraints=constraints
            )
            permission.users.add(user)
            permission.object_types.add(ObjectType.objects.get_for_model(model))
        self.client.force_login(user)
        return user

    def assertJsonError(self, response, status):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertFalse(response.json()["success"])
        self.assertNotIn("traceback", response.json())

    def execution_counts(self):
        return {plan: plan.executions.count() for plan in (self.plan_a, self.plan_b)}


class AnonymousAccessTests(PermissionTestCase):
    def test_endpoints_reject_without_writing(self):
        before = self.execution_counts()
        for url, data in (
            (QUICK_COMPLETE, {"execution_id": self.execution_a.pk}),
            (QUICK_COMPLETE, {"plan_id": self.plan_a.pk, "device_id": self.device.pk}),
            (SCHEDULE, {"plan_id": self.plan_a.pk}),
        ):
            with self.subTest(url=url, data=sorted(data)):
                self.assertJsonError(self.client.post(url, data), 401)
        self.assertEqual(self.execution_counts(), before)
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.status, "scheduled")

    def test_tab_redirects_to_login(self):
        response = self.client.get(reverse(f"{NS}device_maintenance_tab", args=[self.device.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])


class EndpointPermissionTests(PermissionTestCase):
    def test_add_permission_required(self):
        self.login((MaintenancePlan, ["view"], None))
        before = self.execution_counts()
        self.assertJsonError(self.client.post(SCHEDULE, {"plan_id": self.plan_a.pk}), 403)
        self.assertJsonError(
            self.client.post(QUICK_COMPLETE, {"plan_id": self.plan_a.pk, "device_id": self.device.pk}), 403
        )
        self.assertEqual(self.execution_counts(), before)

    def test_change_permission_required(self):
        self.login((MaintenanceExecution, ["view"], None))
        self.assertJsonError(self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk}), 404)
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.status, "scheduled")

    def test_plan_must_be_viewable(self):
        self.login((MaintenancePlan, ["view"], {"name": "A"}), (MaintenanceExecution, ["add"], None))
        self.assertJsonError(self.client.post(SCHEDULE, {"plan_id": self.plan_b.pk}), 404)
        self.assertEqual(self.client.post(SCHEDULE, {"plan_id": self.plan_a.pk}).status_code, 200)

    def test_add_constraints_are_enforced(self):
        self.login(
            (MaintenancePlan, ["view"], None),
            (MaintenanceExecution, ["add"], {"maintenance_plan__name": "A"}),
        )
        for url, extra in ((SCHEDULE, {}), (QUICK_COMPLETE, {"device_id": self.device.pk})):
            with self.subTest(url=url):
                before = self.execution_counts()
                self.assertJsonError(self.client.post(url, {"plan_id": self.plan_b.pk, **extra}), 403)
                self.assertEqual(self.execution_counts(), before)

                response = self.client.post(url, {"plan_id": self.plan_a.pk, **extra})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(self.plan_a.executions.count(), before[self.plan_a] + 1)

    def test_change_constraints_apply_to_the_saved_object(self):
        self.login((MaintenanceExecution, ["change"], {"status": "scheduled"}))
        self.assertJsonError(self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk}), 403)
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.status, "scheduled")
        self.assertIsNone(self.execution_a.completed_date)

    @override_settings(EVENTS_PIPELINE=["netbox_maintenance_device.tests.test_permissions.record_events"])
    def test_rejected_write_fires_no_events(self):
        self.login(
            (MaintenancePlan, ["view"], None),
            (MaintenanceExecution, ["add"], {"maintenance_plan__name": "A"}),
        )
        recorded_events.clear()
        self.assertJsonError(self.client.post(SCHEDULE, {"plan_id": self.plan_b.pk}), 403)
        self.assertEqual(recorded_events, [])

        self.assertEqual(self.client.post(SCHEDULE, {"plan_id": self.plan_a.pk}).status_code, 200)
        self.assertNotEqual(recorded_events, [])


class EndpointBehaviorTests(PermissionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="root", first_name="Grace", last_name="Hopper"
        )
        self.client.force_login(self.user)

    def test_invalid_input_returns_400(self):
        for url, data in (
            (SCHEDULE, {"plan_id": self.plan_a.pk, "scheduled_date": "not-a-date"}),
            (SCHEDULE, {"plan_id": "abc"}),
            (SCHEDULE, {}),
            (QUICK_COMPLETE, {"execution_id": "abc"}),
            (QUICK_COMPLETE, {"plan_id": "abc", "device_id": self.device.pk}),
            (QUICK_COMPLETE, {}),
        ):
            with self.subTest(url=url, data=data):
                self.assertJsonError(self.client.post(url, data), 400)

    def test_missing_objects_return_json_404(self):
        self.assertJsonError(self.client.post(SCHEDULE, {"plan_id": 999999}), 404)
        self.assertJsonError(self.client.post(QUICK_COMPLETE, {"execution_id": 999999}), 404)

    def test_unexpected_errors_are_logged_not_returned(self):
        with patch(
            "netbox_maintenance_device.views.save_restricted", side_effect=RuntimeError("internal detail")
        ), self.assertLogs("netbox.plugins.netbox_maintenance_device", level="ERROR"):
            response = self.client.post(SCHEDULE, {"plan_id": self.plan_a.pk})
        self.assertJsonError(response, 500)
        self.assertNotIn("internal detail", response.content.decode())

    def test_schedule_creates_execution(self):
        response = self.client.post(SCHEDULE, {"plan_id": self.plan_a.pk, "scheduled_date": "2030-01-02"})
        self.assertEqual(response.status_code, 200)
        execution = MaintenanceExecution.objects.get(pk=response.json()["execution_id"])
        self.assertEqual(execution.status, "scheduled")
        self.assertEqual(execution.technician, "Grace Hopper")
        self.assertEqual(execution.scheduled_date.date().isoformat(), "2030-01-02")

    def test_complete_records_prechange_data(self):
        response = self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk})
        self.assertEqual(response.status_code, 200)
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.status, "completed")
        self.assertIsNotNone(self.execution_a.completed_date)

        change = ObjectChange.objects.filter(
            changed_object_id=self.execution_a.pk, action=ObjectChangeActionChoices.ACTION_UPDATE
        ).first()
        self.assertEqual(change.prechange_data["status"], "scheduled")
        self.assertEqual(change.postchange_data["status"], "completed")

    def test_complete_with_blank_technician_keeps_assigned_one(self):
        self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk, "technician": ""})
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.technician, "tech-a")

    def test_complete_without_any_technician_uses_logged_in_user(self):
        MaintenanceExecution.objects.filter(pk=self.execution_a.pk).update(technician="")
        self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk})
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.technician, "Grace Hopper")

    def test_closed_executions_cannot_be_completed(self):
        for status in ("completed", "cancelled"):
            with self.subTest(status=status):
                MaintenanceExecution.objects.filter(pk=self.execution_a.pk).update(status=status)
                self.assertJsonError(self.client.post(QUICK_COMPLETE, {"execution_id": self.execution_a.pk}), 400)
                self.execution_a.refresh_from_db()
                self.assertEqual(self.execution_a.status, status)
                self.assertIsNone(self.execution_a.completed_date)


class ReadPermissionTests(PermissionTestCase):
    def tab(self):
        return self.client.get(reverse(f"{NS}device_maintenance_tab", args=[self.device.pk]))

    def test_tab_is_restricted(self):
        self.login(
            (Device, ["view"], None),
            (MaintenancePlan, ["view"], {"name": "A"}),
            (MaintenanceExecution, ["view"], {"maintenance_plan__name": "A"}),
        )
        response = self.tab()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["maintenance_plans"]), [self.plan_a])
        self.assertEqual(list(response.context["recent_executions"]), [self.execution_a])

    def test_tab_requires_view_on_the_device(self):
        self.login((MaintenancePlan, ["view"], None))
        self.assertEqual(self.tab().status_code, 404)

    def test_device_panel_is_restricted(self):
        self.login((Device, ["view"], None), (MaintenancePlan, ["view"], {"name": "A"}))
        content = self.client.get(self.device.get_absolute_url()).content.decode()
        self.assertIn(self.plan_a.get_absolute_url(), content)
        self.assertNotIn(self.plan_b.get_absolute_url(), content)

    def test_plan_page_hides_executions_without_view_permission(self):
        self.login((MaintenancePlan, ["view"], None))
        content = self.client.get(self.plan_a.get_absolute_url()).content.decode()
        self.assertNotIn("tech-a", content)
        self.assertNotIn(self.execution_a.get_absolute_url(), content)

    def test_plan_page_shows_permitted_executions(self):
        self.login((MaintenancePlan, ["view"], None), (MaintenanceExecution, ["view"], None))
        content = self.client.get(self.plan_a.get_absolute_url()).content.decode()
        self.assertIn("tech-a", content)
        self.assertIn(self.execution_a.get_absolute_url(), content)

    def test_upcoming_counters_are_restricted(self):
        self.login((MaintenancePlan, ["view"], {"name": "A"}))
        response = self.client.get(reverse(f"{NS}upcoming_maintenance"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row.record for row in response.context["table"].rows], [self.plan_a])
        self.assertEqual(response.context["total_plans"], 1)


class ActionButtonTests(PermissionTestCase):
    """Buttons are offered only to users whose request would be allowed."""

    VIEW_ALL = (
        (Device, ["view"], None),
        (MaintenancePlan, ["view"], None),
        (MaintenanceExecution, ["view"], None),
    )

    def pages(self):
        return {
            "tab": reverse(f"{NS}device_maintenance_tab", args=[self.device.pk]),
            "panel": self.device.get_absolute_url(),
            "upcoming": reverse(f"{NS}upcoming_maintenance"),
        }

    def assertButtons(self, *, schedule, complete):
        for name, url in self.pages().items():
            with self.subTest(page=name):
                content = self.client.get(url).content.decode()
                # The tab offers only the quick action for plans and completes from its history.
                self.assertEqual(f'data-plan-id="{self.plan_a.pk}"' in content, schedule)
                self.assertEqual(f'data-execution-id="{self.execution_a.pk}"' in content, complete)

    def test_view_only_user_gets_no_buttons(self):
        self.login(*self.VIEW_ALL)
        self.assertButtons(schedule=False, complete=False)

    def test_add_permission_offers_schedule_only(self):
        self.login(*self.VIEW_ALL, (MaintenanceExecution, ["add"], None))
        self.assertButtons(schedule=True, complete=False)

    def test_change_permission_offers_complete_only(self):
        self.login(*self.VIEW_ALL, (MaintenanceExecution, ["change"], None))
        self.assertButtons(schedule=False, complete=True)
