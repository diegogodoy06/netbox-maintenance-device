from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from .models import MaintenancePlan, MaintenanceNotification
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_maintenance_notifications(days_ahead=7):
    """
    Celery task to check for overdue and upcoming maintenance and create notifications
    This task should be scheduled to run periodically (e.g., daily)
    """
    logger.info(f'Checking maintenance plans (looking {days_ahead} days ahead)...')
    
    # Get all active maintenance plans
    active_plans = MaintenancePlan.objects.filter(is_active=True)
    
    notifications_created = 0
    
    for plan in active_plans:
        try:
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
                    # Create overdue notifications
                    created_notifications = plan.create_notification(
                        notification_type='overdue',
                        priority='critical',
                        title=_('Overdue Maintenance: {}').format(plan.name),
                        message=_('Device {} has overdue maintenance "{}" (overdue by {} days)').format(
                            plan.device.name, plan.name, days_overdue
                        )
                    )
                    notifications_created += len(created_notifications)
                    logger.info(f'Created {len(created_notifications)} overdue notifications for plan: {plan.name}')
            
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
                    priority = 'high' if days_until <= 3 else 'medium'
                    
                    # Create due soon notifications
                    created_notifications = plan.create_notification(
                        notification_type='due_soon',
                        priority=priority,
                        title=_('Upcoming Maintenance: {}').format(plan.name),
                        message=_('Device {} has maintenance "{}" due in {} days').format(
                            plan.device.name, plan.name, days_until
                        )
                    )
                    notifications_created += len(created_notifications)
                    logger.info(f'Created {len(created_notifications)} due soon notifications for plan: {plan.name}')
                    
        except Exception as e:
            logger.error(f'Error processing maintenance plan {plan.id}: {str(e)}')
            continue
    
    # Clean up old read notifications (older than 30 days)
    try:
        old_notifications = MaintenanceNotification.objects.filter(
            is_read=True,
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        deleted_count = old_notifications.count()
        old_notifications.delete()
        logger.info(f'Cleaned up {deleted_count} old notifications')
    except Exception as e:
        logger.error(f'Error cleaning up old notifications: {str(e)}')
    
    logger.info(f'Task completed. Created {notifications_created} notifications')
    return {
        'notifications_created': notifications_created,
        'task_completed_at': timezone.now().isoformat()
    }


@shared_task
def send_browser_notifications():
    """
    Celery task to send browser notifications for unread maintenance notifications
    This task should be scheduled to run frequently (e.g., every 5 minutes)
    """
    logger.info('Checking for unsent browser notifications...')
    
    # Get unread notifications that haven't been sent to browser yet
    unsent_notifications = MaintenanceNotification.objects.filter(
        is_read=False,
        is_sent_browser=False,
        created_at__gte=timezone.now() - timedelta(hours=24)  # Only recent notifications
    )
    
    sent_count = 0
    
    for notification in unsent_notifications:
        try:
            # Mark as sent to browser (will be handled by frontend JavaScript)
            notification.is_sent_browser = True
            notification.save()
            sent_count += 1
            
        except Exception as e:
            logger.error(f'Error marking notification {notification.id} as sent: {str(e)}')
            continue
    
    logger.info(f'Marked {sent_count} notifications for browser sending')
    return {
        'notifications_marked': sent_count,
        'task_completed_at': timezone.now().isoformat()
    }
