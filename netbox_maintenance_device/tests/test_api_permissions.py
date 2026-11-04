"""Authentication and object permission coverage for the plugin's REST API."""

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from users.models import Token

from netbox_maintenance_device.models import MaintenanceExecution, MaintenancePlan
from netbox_maintenance_device.tests.test_permissions import PermissionTestCase

API = "plugins-api:netbox_maintenance_device-api:"


def url(name, *args):
    return reverse(f"{API}{name}", args=args)


class ApiTestCase(PermissionTestCase):
    def api_for(self, *grants):
        api = APIClient()
        api.force_authenticate(self.login(*grants))
        return api


class TokenWriteAccessTests(ApiTestCase):
    ALL_ACTIONS = ["view", "add", "change", "delete"]

    def client_with_token(self, write_enabled):
        """Authenticate through a real Authorization header."""
        user = self.login(
            (MaintenancePlan, self.ALL_ACTIONS, None),
            (MaintenanceExecution, self.ALL_ACTIONS, None),
        )
        self.client.logout()
        fields = {field.name for field in Token._meta.get_fields()}
        # NetBox 4.5+ defaults to v2 tokens, which the plaintext header doesn't identify.
        options = {"version": 1} if "version" in fields else {}
        token = Token.objects.create(user=user, write_enabled=write_enabled, **options)
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f"Token {getattr(token, 'plaintext', None) or token.key}")
        return api

    def writes(self, api):
        """Yield (label, response) for one request to each kind of write route."""
        now = timezone.now().isoformat()
        yield "create", api.post(
            url("maintenanceexecution-list"),
            {"maintenance_plan": self.plan_a.pk, "scheduled_date": now, "status": "scheduled"},
            format="json",
        )
        yield "update", api.patch(
            url("maintenanceplan-detail", self.plan_a.pk), {"description": "changed"}, format="json"
        )
        yield "schedule", api.post(
            url("maintenanceplan-schedule-maintenance", self.plan_a.pk), {"scheduled_date": now}, format="json"
        )
        yield "complete", api.post(url("maintenanceexecution-complete", self.execution_a.pk), format="json")
        yield "cancel", api.post(url("maintenanceexecution-cancel", self.execution_b.pk), format="json")
        yield "delete", api.delete(url("maintenanceexecution-detail", self.execution_b.pk))

    def test_read_only_token_cannot_write(self):
        api = self.client_with_token(write_enabled=False)
        before = self.execution_counts()
        for label, response in self.writes(api):
            with self.subTest(route=label):
                self.assertEqual(response.status_code, 403)

        self.assertEqual(self.execution_counts(), before)
        self.plan_a.refresh_from_db()
        self.assertEqual(self.plan_a.description, "")
        self.execution_a.refresh_from_db()
        self.assertEqual(self.execution_a.status, "scheduled")

    def test_read_only_token_can_read(self):
        api = self.client_with_token(write_enabled=False)
        self.assertEqual(api.get(url("maintenanceplan-list")).status_code, 200)
        self.assertEqual(api.get(url("maintenanceexecution-detail", self.execution_a.pk)).status_code, 200)

    def test_write_enabled_token_can_write(self):
        api = self.client_with_token(write_enabled=True)
        expected = {"create": 201, "update": 200, "schedule": 201, "complete": 200, "cancel": 200, "delete": 204}
        for label, response in self.writes(api):
            with self.subTest(route=label):
                self.assertEqual(response.status_code, expected[label])


class CustomActionPermissionTests(ApiTestCase):
    def schedule(self, api, plan):
        return api.post(
            url("maintenanceplan-schedule-maintenance", plan.pk),
            {"scheduled_date": timezone.now().isoformat()},
            format="json",
        )

    def test_anonymous_is_rejected(self):
        api = APIClient()
        self.assertIn(self.schedule(api, self.plan_a).status_code, (401, 403))
        self.assertIn(
            api.post(url("maintenanceexecution-complete", self.execution_a.pk)).status_code, (401, 403)
        )

    def test_complete_and_cancel_need_only_change(self):
        api = self.api_for((MaintenanceExecution, ["change"], None))
        response = api.post(url("maintenanceexecution-complete", self.execution_a.pk), format="json")
        self.assertEqual(response.status_code, 200, response.content)
        response = api.post(url("maintenanceexecution-cancel", self.execution_b.pk), format="json")
        self.assertEqual(response.status_code, 200, response.content)

    def test_complete_and_cancel_require_change(self):
        api = self.api_for((MaintenanceExecution, ["view", "add"], None))
        for name in ("complete", "cancel"):
            with self.subTest(action=name):
                response = api.post(url(f"maintenanceexecution-{name}", self.execution_a.pk), format="json")
                self.assertEqual(response.status_code, 403)

    def test_change_constraints_select_the_execution(self):
        api = self.api_for(
            (MaintenanceExecution, ["change"], {"maintenance_plan__name": "A"}),
            (MaintenanceExecution, ["add"], None),
        )
        for name in ("complete", "cancel"):
            with self.subTest(action=name):
                response = api.post(url(f"maintenanceexecution-{name}", self.execution_b.pk), format="json")
                self.assertEqual(response.status_code, 404)
                self.execution_b.refresh_from_db()
                self.assertEqual(self.execution_b.status, "scheduled")

    def test_change_constraints_apply_to_the_saved_object(self):
        api = self.api_for((MaintenanceExecution, ["change"], {"status": "scheduled"}))
        for name in ("complete", "cancel"):
            with self.subTest(action=name):
                response = api.post(url(f"maintenanceexecution-{name}", self.execution_a.pk), format="json")
                self.assertEqual(response.status_code, 403)
                self.execution_a.refresh_from_db()
                self.assertEqual(self.execution_a.status, "scheduled")

    def test_complete_records_prechange_data(self):
        api = self.api_for((MaintenanceExecution, ["change"], None))
        api.post(url("maintenanceexecution-complete", self.execution_a.pk), format="json")
        change = ObjectChange.objects.filter(
            changed_object_id=self.execution_a.pk, action=ObjectChangeActionChoices.ACTION_UPDATE
        ).first()
        self.assertEqual(change.prechange_data["status"], "scheduled")
        self.assertEqual(change.postchange_data["status"], "completed")

    def test_schedule_needs_view_on_plan_and_add_on_execution(self):
        api = self.api_for((MaintenancePlan, ["view"], None), (MaintenanceExecution, ["add"], None))
        self.assertEqual(self.schedule(api, self.plan_a).status_code, 201)

    def test_schedule_requires_a_viewable_plan(self):
        api = self.api_for((MaintenancePlan, ["view"], {"name": "A"}), (MaintenanceExecution, ["add"], None))
        self.assertEqual(self.schedule(api, self.plan_b).status_code, 404)

    def test_schedule_enforces_add_constraints(self):
        api = self.api_for(
            (MaintenancePlan, ["view"], None),
            (MaintenanceExecution, ["add"], {"maintenance_plan__name": "A"}),
        )
        before = self.plan_b.executions.count()
        self.assertEqual(self.schedule(api, self.plan_b).status_code, 403)
        self.assertEqual(self.plan_b.executions.count(), before)
        self.assertEqual(self.schedule(api, self.plan_a).status_code, 201)


class PlanSerializerVisibilityTests(ApiTestCase):
    def get_plan(self, api):
        response = api.get(url("maintenanceplan-detail", self.plan_a.pk))
        self.assertEqual(response.status_code, 200)
        return response.data

    def complete_execution_a(self):
        MaintenanceExecution.objects.filter(pk=self.execution_a.pk).update(
            status="completed", completed=True, completed_date=timezone.now()
        )

    def test_executions_hidden_without_view_permission(self):
        self.complete_execution_a()
        data = self.get_plan(self.api_for((MaintenancePlan, ["view"], None)))
        self.assertEqual(list(data["executions"]), [])
        self.assertEqual(data["execution_count"], 0)
        self.assertIsNone(data["last_execution_date"])

    def test_executions_shown_with_view_permission(self):
        self.complete_execution_a()
        data = self.get_plan(self.api_for((MaintenancePlan, ["view"], None), (MaintenanceExecution, ["view"], None)))
        self.assertEqual([execution["id"] for execution in data["executions"]], [self.execution_a.pk])
        self.assertEqual(data["execution_count"], 1)
        self.assertIsNotNone(data["last_execution_date"])

    def test_list_route_applies_the_same_restriction(self):
        api = self.api_for((MaintenancePlan, ["view"], None))
        for plan in api.get(url("maintenanceplan-list")).data["results"]:
            self.assertEqual(list(plan["executions"]), [])

    def test_serializing_outside_a_request_includes_all_executions(self):
        from extras.events import serialize_for_event

        data = serialize_for_event(self.plan_a)
        self.assertEqual([execution["id"] for execution in data["executions"]], [self.execution_a.pk])
