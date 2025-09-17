"""
Signal handlers for NetBox Maintenance Device plugin.

This module contains Django signal handlers that are automatically
executed when certain events occur in NetBox.
"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def auto_heal_after_migrate(sender, **kwargs):
    """
    Automatically heal database issues after migrations are complete.
    
    This signal handler is triggered after Django migrations run,
    ensuring that any database cleanup happens at the right time.
    """
    # Only run for our app
    if sender.name == 'netbox_maintenance_device':
        try:
            from .database_healer import auto_heal_database
            logger.info("NetBox Maintenance Device: Running post-migration auto-heal...")
            auto_heal_database()
        except Exception as e:
            logger.warning(f"NetBox Maintenance Device: Post-migration auto-heal failed: {e}")


class NetboxMaintenanceDeviceConfig(AppConfig):
    """
    Django app configuration for automatic signal registration.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'netbox_maintenance_device'
    verbose_name = 'NetBox Maintenance Device'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        # Import signals to register them
        try:
            from . import signals  # This file
        except ImportError:
            pass