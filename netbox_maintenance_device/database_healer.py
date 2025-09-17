"""
Auto-healing functionality for NetBox Maintenance Device plugin.

This module provides automatic detection and resolution of common database
integrity issues that may occur when upgrading from previous versions.
"""

from django.db import connection
from django.core.management.color import no_style
import logging

logger = logging.getLogger(__name__)


class DatabaseHealer:
    """
    Automatically detect and heal common database issues.
    """
    
    @staticmethod
    def check_and_heal_orphaned_tables():
        """
        Check for and automatically heal orphaned notification table issues.
        
        This method is called during plugin initialization to ensure
        database integrity and prevent IntegrityError exceptions.
        """
        try:
            with connection.cursor() as cursor:
                # Check if the problematic table exists
                table_exists = DatabaseHealer._check_notification_table_exists(cursor)
                
                if table_exists:
                    logger.warning(
                        "NetBox Maintenance Device: Detected orphaned notification table. "
                        "Attempting automatic cleanup..."
                    )
                    
                    success = DatabaseHealer._cleanup_notification_table(cursor)
                    
                    if success:
                        logger.info(
                            "NetBox Maintenance Device: Successfully cleaned up orphaned table. "
                            "Plugin should now function normally."
                        )
                    else:
                        logger.error(
                            "NetBox Maintenance Device: Failed to cleanup orphaned table. "
                            "Manual intervention may be required."
                        )
                else:
                    logger.debug("NetBox Maintenance Device: Database structure is clean.")
                    
        except Exception as e:
            logger.warning(f"NetBox Maintenance Device: Auto-healing check failed: {e}")
    
    @staticmethod
    def _check_notification_table_exists(cursor):
        """Check if the orphaned notification table exists."""
        try:
            # Try a simple query that would fail if table doesn't exist
            cursor.execute(
                "SELECT 1 FROM netbox_maintenance_device_maintenancenotification LIMIT 1;"
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def _cleanup_notification_table(cursor):
        """Safely cleanup the orphaned notification table."""
        try:
            # Get database type
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()[0]
            is_postgresql = 'PostgreSQL' in db_version
            
            # Count existing records for logging
            cursor.execute("SELECT COUNT(*) FROM netbox_maintenance_device_maintenancenotification;")
            record_count = cursor.fetchone()[0]
            
            if record_count > 0:
                logger.info(f"NetBox Maintenance Device: Removing {record_count} orphaned notification records")
            
            # Remove all records first
            cursor.execute("DELETE FROM netbox_maintenance_device_maintenancenotification;")
            
            # Drop constraints for PostgreSQL
            if is_postgresql:
                try:
                    cursor.execute("""
                        SELECT constraint_name 
                        FROM information_schema.table_constraints 
                        WHERE table_name = 'netbox_maintenance_device_maintenancenotification'
                        AND constraint_type = 'FOREIGN KEY';
                    """)
                    
                    constraints = cursor.fetchall()
                    for constraint_row in constraints:
                        constraint_name = constraint_row[0]
                        cursor.execute(f"""
                            ALTER TABLE netbox_maintenance_device_maintenancenotification 
                            DROP CONSTRAINT IF EXISTS "{constraint_name}";
                        """)
                        logger.debug(f"NetBox Maintenance Device: Dropped constraint {constraint_name}")
                        
                except Exception as e:
                    logger.warning(f"NetBox Maintenance Device: Could not drop constraints: {e}")
            
            # Drop the table
            cursor.execute("DROP TABLE IF EXISTS netbox_maintenance_device_maintenancenotification;")
            
            return True
            
        except Exception as e:
            logger.error(f"NetBox Maintenance Device: Cleanup failed: {e}")
            return False


def auto_heal_database():
    """
    Public function to trigger automatic database healing.
    
    This can be called during plugin initialization or from management commands.
    """
    DatabaseHealer.check_and_heal_orphaned_tables()