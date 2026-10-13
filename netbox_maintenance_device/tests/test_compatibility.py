"""Integration coverage executed inside a real NetBox installation.

Run with NetBox's manage.py, PostgreSQL and Redis; no NetBox modules are stubbed.
Only outbound webhook delivery and its queue boundary are mocked.
"""

from datetime import timedelta
from io import StringIO
from unittest.mock import Mock, patch
from uuid import uuid4

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework.test import APIClient

from core.choices import JobIntervalChoices
from core.models import Job, ObjectType
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.choices import CustomFieldTypeChoices, EventRuleActionChoices
from extras.events import flush_events
from extras.forms import EventRuleForm
from extras.models import (
    CustomField,
    CustomFieldChoiceSet,
    EventRule,
    Notification,
    NotificationGroup,
    Tag,
    Webhook,
)
from netbox.context import current_request, events_queue
from netbox.registry import registry
from virtualization.models import VirtualMachine

from netbox_maintenance_device.events import fire_event
from netbox_maintenance_device.forms import MaintenancePlanForm
from netbox_maintenance_device.jobs import CheckMaintenanceJob
from netbox_maintenance_device.models import MaintenanceExecution, MaintenancePlan


class CompatibilityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="maintenance-admin", password="test-only-password"
        )
        site = Site.objects.create(name="Maintenance site", slug="maintenance-site")
        manufacturer = Manufacturer.objects.create(name="Test vendor", slug="test-vendor")
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model="Test model", slug="test-model"
        )
        role = DeviceRole.objects.create(name="Test role", slug="test-role")
        cls.device = Device.objects.create(
            name="Maintenance device", site=site, device_type=device_type, role=role
        )
        cls.vm = VirtualMachine.objects.create(name="Maintenance VM")
        cls.plan = MaintenancePlan.objects.create(
            device=cls.device, name="Device plan", frequency_days=30
        )
        cls.vm_plan = MaintenancePlan.objects.create(
            virtual_machine=cls.vm, name="VM plan", frequency_days=1, frequency_unit="months"
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.api = APIClient()
        self.api.force_authenticate(self.user)

    def api_url(self, model, pk=None, action=None):
        suffix = action or ("detail" if pk else "list")
        kwargs = {"pk": pk} if pk else None
        return reverse(f"plugins-api:netbox_maintenance_device-api:{model}-{suffix}", kwargs=kwargs)

    def create_rule(self, model, event_types, action_object, action_type):
        rule = EventRule.objects.create(
            name=f"Maintenance rule {EventRule.objects.count()}",
            event_types=event_types,
            action_type=action_type,
            action_object_type=ObjectType.objects.get_for_model(action_object),
            action_object_id=action_object.pk,
        )
        rule.object_types.add(ObjectType.objects.get_for_model(model))
        return rule

    def notification_group(self):
        group = NotificationGroup.objects.create(name="Maintenance operators")
        group.users.add(self.user)
        return group

    def make_overdue(self):
        MaintenancePlan.objects.filter(pk=self.plan.pk).update(
            created=timezone.now() - timedelta(days=60)
        )
        self.plan.refresh_from_db()

    def test_plugin_is_loaded_and_job_registered(self):
        self.assertTrue(apps.is_installed("netbox_maintenance_device"))
        self.assertIn("netbox_maintenance_device", registry["plugins"]["installed"])
        self.assertEqual(
            registry["system_jobs"][CheckMaintenanceJob]["interval"],
            JobIntervalChoices.INTERVAL_DAILY,
        )

    def test_event_types_available_in_event_rule_form(self):
        choices = {choice[0] for choice in EventRuleForm().fields["event_types"].choices}
        for name in ("maintenance_due", "maintenance_scheduled", "maintenance_completed"):
            with self.subTest(event_type=name):
                self.assertIn(name, choices)
                self.assertTrue(str(registry["event_types"][name]))

    def test_plan_forms_accept_device_and_vm(self):
        for target_field, target in (("device", self.device), ("virtual_machine", self.vm)):
            with self.subTest(target=target_field):
                form = MaintenancePlanForm(
                    data={
                        target_field: target.pk,
                        "name": "Form plan",
                        "frequency_days": 2,
                        "frequency_unit": "months",
                        "maintenance_type": "preventive",
                        "is_active": True,
                    }
                )
                self.assertTrue(form.is_valid(), form.errors.as_json())
                plan = form.save()
                self.assertEqual(plan.target, target)

    def test_plan_form_rejects_two_targets(self):
        form = MaintenancePlanForm(
            data={
                "device": self.device.pk,
                "virtual_machine": self.vm.pk,
                "name": "Invalid plan",
                "frequency_days": 1,
                "frequency_unit": "days",
                "maintenance_type": "preventive",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_ui_pages_and_core_extensions_render(self):
        execution = MaintenanceExecution.objects.create(
            maintenance_plan=self.plan, scheduled_date=timezone.now()
        )
        urls = [
            reverse("plugins:netbox_maintenance_device:maintenanceplan_list"),
            reverse("plugins:netbox_maintenance_device:maintenanceexecution_list"),
            reverse("plugins:netbox_maintenance_device:upcoming_maintenance"),
            reverse("plugins:netbox_maintenance_device:maintenanceplan_add"),
            reverse("plugins:netbox_maintenance_device:maintenanceexecution_add"),
            reverse("plugins:netbox_maintenance_device:maintenanceplan", args=[self.plan.pk]),
            reverse("plugins:netbox_maintenance_device:maintenanceplan", args=[self.vm_plan.pk]),
            reverse("plugins:netbox_maintenance_device:maintenanceplan_edit", args=[self.plan.pk]),
            reverse("plugins:netbox_maintenance_device:maintenanceexecution", args=[execution.pk]),
            reverse(
                "plugins:netbox_maintenance_device:device_maintenance_tab", args=[self.device.pk]
            ),
            reverse(
                "plugins:netbox_maintenance_device:virtualmachine_maintenance_tab",
                args=[self.vm.pk],
            ),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        for view, target in (
            ("dcim:device", self.device),
            ("virtualization:virtualmachine", self.vm),
        ):
            with self.subTest(view=view):
                response = self.client.get(reverse(view, args=[target.pk]))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, target.maintenance_plans.first().name)

    def test_api_create_read_update_delete_for_device_and_vm(self):
        for target_field, target in (("device", self.device), ("virtual_machine", self.vm)):
            with self.subTest(target=target_field):
                response = self.api.post(
                    self.api_url("maintenanceplan"),
                    {
                        target_field: target.pk,
                        "name": "API plan",
                        "frequency_days": 2,
                        "frequency_unit": "quarters",
                    },
                    format="json",
                )
                self.assertEqual(response.status_code, 201, response.data)
                pk = response.data["id"]
                self.assertEqual(response.data[target_field]["id"], target.pk)
                detail_url = self.api_url("maintenanceplan", pk)
                response = self.api.get(detail_url)
                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual(response.data["execution_count"], 0)
                response = self.api.patch(detail_url, {"frequency_days": 3}, format="json")
                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual(response.data["frequency_days"], 3)
                self.assertEqual(self.api.delete(detail_url).status_code, 204)

    def test_api_schedule_complete_cancel(self):
        for plan in (self.plan, self.vm_plan):
            with self.subTest(plan=plan.name):
                response = self.api.post(
                    self.api_url("maintenanceplan", plan.pk, "schedule-maintenance"),
                    {"scheduled_date": timezone.now().isoformat(), "technician": "Operator"},
                    format="json",
                )
                self.assertEqual(response.status_code, 201, response.data)
                pk = response.data["id"]
                response = self.api.post(self.api_url("maintenanceexecution", pk, "complete"))
                self.assertEqual(response.status_code, 200, response.data)
                self.assertTrue(response.data["completed"])
                execution = MaintenanceExecution.objects.create(
                    maintenance_plan=plan, scheduled_date=timezone.now()
                )
                response = self.api.post(
                    self.api_url("maintenanceexecution", execution.pk, "cancel")
                )
                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual(response.data["status"], "cancelled")

    def test_api_bulk_create(self):
        response = self.api.post(
            self.api_url("maintenanceplan"),
            [
                {"device": self.device.pk, "name": "Bulk device", "frequency_days": 7},
                {"virtual_machine": self.vm.pk, "name": "Bulk VM", "frequency_days": 7},
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(len(response.data), 2)

    def test_api_schedule_rejects_invalid_datetime_without_writing(self):
        before = MaintenanceExecution.objects.count()
        response = self.api.post(
            self.api_url("maintenanceplan", self.plan.pk, "schedule-maintenance"),
            {"scheduled_date": "invalid-date"},
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertIn("scheduled_date", response.data)
        self.assertEqual(MaintenanceExecution.objects.count(), before)

    def test_api_target_filters(self):
        for field, target, plan in (
            ("device_id", self.device, self.plan),
            ("virtual_machine_id", self.vm, self.vm_plan),
        ):
            with self.subTest(field=field):
                response = self.api.get(self.api_url("maintenanceplan"), {field: target.pk})
                self.assertEqual(response.status_code, 200, response.data)
                self.assertEqual([item["id"] for item in response.data["results"]], [plan.pk])

    def test_tags_and_selection_custom_field_data_survive_api_updates(self):
        choices = CustomFieldChoiceSet.objects.create(
            name="Maintenance locations", extra_choices=[["lab", "Lab"], ["dc", "Data Center"]]
        )
        field = CustomField.objects.create(
            name="maintenance_location",
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choices,
        )
        field.object_types.add(ObjectType.objects.get_for_model(MaintenancePlan))
        tag = Tag.objects.create(name="Maintenance tag", slug="maintenance-tag")
        response = self.api.patch(
            self.api_url("maintenanceplan", self.plan.pk),
            {
                "tags": [tag.pk],
                "custom_field_data": {field.name: "dc"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["custom_field_data"][field.name], "dc")
        self.assertEqual(response.data["tags"][0]["id"], tag.pk)
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.custom_field_data[field.name], "dc")

    def test_api_invalid_bulk_write_is_atomic(self):
        before = MaintenancePlan.objects.count()
        response = self.api.post(
            self.api_url("maintenanceplan"),
            [
                {"device": self.device.pk, "name": "Valid bulk plan", "frequency_days": 7},
                {"device": self.device.pk, "name": "Invalid bulk plan", "frequency_days": 0},
            ],
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(MaintenancePlan.objects.count(), before)

    def test_api_requires_authentication(self):
        self.assertIn(APIClient().get(self.api_url("maintenanceplan")).status_code, (401, 403))

    def test_scheduled_and_completed_notifications(self):
        self.create_rule(
            MaintenanceExecution,
            ["maintenance_scheduled", "maintenance_completed"],
            self.notification_group(),
            EventRuleActionChoices.NOTIFICATION,
        )
        execution = MaintenanceExecution.objects.create(
            maintenance_plan=self.plan, scheduled_date=timezone.now()
        )
        notification = Notification.objects.get(object_id=execution.pk)
        self.assertEqual(notification.event_type, "maintenance_scheduled")
        execution.status = "completed"
        execution.completed_date = timezone.now()
        execution.save()
        notification.refresh_from_db()
        self.assertEqual(notification.event_type, "maintenance_completed")

    def test_request_queue_preserves_distinct_custom_events(self):
        request = RequestFactory().post("/maintenance-test/")
        request.user = self.user
        request.id = uuid4()
        queue = {}
        request_token = current_request.set(request)
        queue_token = events_queue.set(queue)
        try:
            fire_event(self.plan, "maintenance_due")
            fire_event(self.plan, "maintenance_scheduled")
        finally:
            events_queue.reset(queue_token)
            current_request.reset(request_token)
        self.assertEqual(len(queue), 2)
        self.assertEqual(
            {event["event_type"] for event in queue.values()},
            {"maintenance_due", "maintenance_scheduled"},
        )
        for event in queue.values():
            self.assertEqual(event["data"]["id"], self.plan.pk)
            self.assertEqual(event["request"], request)
            self.assertIn("postchange", event["snapshots"])

    def test_webhook_from_request_and_background_contexts(self):
        webhook = Webhook.objects.create(
            name="Maintenance webhook",
            payload_url="https://example.com/maintenance",
            body_template="{{ event }}:{{ data.id }}",
        )
        self.create_rule(
            MaintenancePlan, ["maintenance_due"], webhook, EventRuleActionChoices.WEBHOOK
        )
        # NetBox 4.7 moved action dispatch into extras.event_rules. Mock only the
        # external queue boundary and exercise the real processor on both APIs.
        try:
            import extras.event_rules  # noqa: F401

            queue_path = "extras.event_rules.get_queue"
        except ImportError:
            queue_path = "extras.events.get_queue"
        request = RequestFactory().post("/maintenance-test/")
        request.user = self.user
        request.id = uuid4()
        for context_request in (None, request):
            with self.subTest(background=context_request is None), patch(queue_path) as get_queue:
                if context_request is None:
                    fire_event(self.plan, "maintenance_due")
                else:
                    queue = {}
                    token = events_queue.set(queue)
                    try:
                        fire_event(self.plan, "maintenance_due", request=context_request)
                        flush_events(list(queue.values()))
                    finally:
                        events_queue.reset(token)
                get_queue.return_value.enqueue.assert_called_once()
                args, kwargs = get_queue.return_value.enqueue.call_args
                self.assertEqual(kwargs["data"]["id"], self.plan.pk)
                kwargs.pop("retry", None)  # Consumed by RQ, not passed to the job.
                with patch("requests.Session.send", return_value=Mock(status_code=200)) as send:
                    import_string(args[0])(**kwargs)
                self.assertEqual(
                    send.call_args.args[0].body.decode(), f"maintenance_due:{self.plan.pk}"
                )

    def test_overdue_management_command_notifies_once(self):
        self.make_overdue()
        self.create_rule(
            MaintenancePlan,
            ["maintenance_due"],
            self.notification_group(),
            EventRuleActionChoices.NOTIFICATION,
        )
        for _ in range(2):
            call_command("check_maintenance", stdout=StringIO())
        self.plan.refresh_from_db()
        self.assertEqual(self.plan.last_notified_date, self.plan.get_next_maintenance_date().date())
        self.assertEqual(Notification.objects.filter(event_type="maintenance_due").count(), 1)

    def test_daily_job_skips_scheduled_plans(self):
        self.make_overdue()
        MaintenanceExecution.objects.create(
            maintenance_plan=self.plan, scheduled_date=timezone.now()
        )
        job = Job.objects.create(name="Maintenance compatibility test", job_id=uuid4())
        runner = CheckMaintenanceJob(job)
        self.addCleanup(runner.logger.removeHandler, runner.logger.handlers[-1])
        runner.run()
        self.plan.refresh_from_db()
        self.assertIsNone(self.plan.last_notified_date)

    def test_daily_job_notifies_overdue_plans(self):
        self.make_overdue()
        self.create_rule(
            MaintenancePlan,
            ["maintenance_due"],
            self.notification_group(),
            EventRuleActionChoices.NOTIFICATION,
        )
        job = Job.objects.create(name="Maintenance compatibility test", job_id=uuid4())
        runner = CheckMaintenanceJob(job)
        self.addCleanup(runner.logger.removeHandler, runner.logger.handlers[-1])
        runner.run()
        runner.run()
        self.assertEqual(Notification.objects.filter(event_type="maintenance_due").count(), 1)
