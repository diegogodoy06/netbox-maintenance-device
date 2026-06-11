from django.core.management.base import BaseCommand
from django.utils import timezone
from netbox_maintenance_device.models import MaintenancePlan
from netbox_maintenance_device.events import fire_event


class Command(BaseCommand):
    help = 'Check for active maintenance plans that are overdue and trigger notifications'

    def handle(self, *args, **options):
        self.stdout.write('Checking maintenance plans...')
        
        active_plans = MaintenancePlan.objects.filter(is_active=True)
        overdue_count = 0
        notified_count = 0
        
        for plan in active_plans:
            if plan.is_overdue():
                overdue_count += 1
                next_due = plan.get_next_maintenance_date()
                if next_due:
                    next_due_date = next_due.date()
                    # Check if we already notified for this specific due date
                    if plan.last_notified_date != next_due_date:
                        # Check if there is already a scheduled execution to avoid spamming
                        has_scheduled = plan.executions.filter(status='scheduled').exists()
                        if not has_scheduled:
                            self.stdout.write(self.style.WARNING(
                                f'Plan "{plan}" is overdue (due since {next_due_date})'
                            ))
                            fire_event(plan, 'maintenance_due')
                            plan.last_notified_date = next_due_date
                            plan.save(update_fields=['last_notified_date'])
                            notified_count += 1
                            
        self.stdout.write(self.style.SUCCESS(
            f'Check complete. Active plans: {active_plans.count()}, Overdue: {overdue_count}, Notified: {notified_count}'
        ))
