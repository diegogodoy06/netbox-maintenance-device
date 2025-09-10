from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from netbox_maintenance_device.models import MaintenancePlan, MaintenanceNotification
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Check for overdue and upcoming maintenance and create notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Days ahead to check for upcoming maintenance (default: 7)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without creating notifications'
        )

    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Checking maintenance plans (looking {days_ahead} days ahead)...')
        )
        
        # Get all active maintenance plans
        active_plans = MaintenancePlan.objects.filter(is_active=True)
        
        notifications_created = 0
        
        for plan in active_plans:
            # Check if plan is overdue
            if plan.is_overdue():
                days_overdue = abs(plan.days_until_due()) if plan.days_until_due() else 0
                
                # Check if we already notified about this overdue maintenance today
                existing_notification = MaintenanceNotification.objects.filter(
                    maintenance_plan=plan,
                    notification_type='overdue',
                    created_at__date=timezone.now().date()
                ).exists()
                
                if not existing_notification:
                    # Get device administrators or fallback to superusers
                    users_to_notify = self.get_users_to_notify(plan)
                    
                    for user in users_to_notify:
                        if not dry_run:
                            notification = MaintenanceNotification.objects.create(
                                user=user,
                                maintenance_plan=plan,
                                notification_type='overdue',
                                priority='critical',
                                title=_('Overdue Maintenance: {}').format(plan.name),
                                message=_('Device {} has overdue maintenance "{}" (overdue by {} days)').format(
                                    plan.device.name, plan.name, days_overdue
                                )
                            )
                            notifications_created += 1
                            
                        self.stdout.write(
                            self.style.WARNING(
                                f'{"[DRY RUN] " if dry_run else ""}Created overdue notification for {user.username}: {plan.device.name} - {plan.name}'
                            )
                        )
            
            # Check if maintenance is due soon
            elif plan.days_until_due() is not None and plan.days_until_due() <= days_ahead:
                days_until = plan.days_until_due()
                
                # Check if we already notified about this upcoming maintenance recently
                existing_notification = MaintenanceNotification.objects.filter(
                    maintenance_plan=plan,
                    notification_type='due_soon',
                    created_at__gte=timezone.now() - timedelta(days=2)
                ).exists()
                
                if not existing_notification:
                    users_to_notify = self.get_users_to_notify(plan)
                    
                    priority = 'high' if days_until <= 3 else 'medium'
                    
                    for user in users_to_notify:
                        if not dry_run:
                            notification = MaintenanceNotification.objects.create(
                                user=user,
                                maintenance_plan=plan,
                                notification_type='due_soon',
                                priority=priority,
                                title=_('Upcoming Maintenance: {}').format(plan.name),
                                message=_('Device {} has maintenance "{}" due in {} days').format(
                                    plan.device.name, plan.name, days_until
                                )
                            )
                            notifications_created += 1
                            
                        self.stdout.write(
                            self.style.WARNING(
                                f'{"[DRY RUN] " if dry_run else ""}Created due soon notification for {user.username}: {plan.device.name} - {plan.name} (in {days_until} days)'
                            )
                        )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would create {notifications_created} notifications')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created {notifications_created} notifications')
            )
            
            # Clean up old read notifications (older than 30 days)
            old_notifications = MaintenanceNotification.objects.filter(
                is_read=True,
                created_at__lt=timezone.now() - timedelta(days=30)
            )
            deleted_count = old_notifications.count()
            old_notifications.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {deleted_count} old notifications')
            )

    def get_users_to_notify(self, plan):
        """Get users that should be notified for this maintenance plan"""
        users = []
        
        # Try to get device administrators (if your NetBox has custom fields or relations)
        # This is a simplified version - you might want to customize based on your setup
        
        # For now, notify superusers and staff users
        # You can customize this logic based on your organization's structure
        users = User.objects.filter(
            is_active=True,
            is_staff=True
        )
        
        # If no staff users, notify superusers as fallback
        if not users.exists():
            users = User.objects.filter(
                is_active=True,
                is_superuser=True
            )
        
        return users
