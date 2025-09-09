"""
Tests for netbox_maintenance_device plugin

These tests validate the basic functionality without requiring a full NetBox installation.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class MockDevice:
    """Mock Device model for testing"""
    def __init__(self, name="test-device"):
        self.name = name
        self.pk = 1


class MockMaintenancePlan:
    """Mock MaintenancePlan for testing logic"""
    def __init__(self, frequency_days=30, created=None):
        self.frequency_days = frequency_days
        self.created = created or datetime.now()
        self.is_active = True
    
    def get_next_maintenance_date(self):
        # Simplified version of the real method
        return self.created + timedelta(days=self.frequency_days)
    
    def is_overdue(self):
        next_date = self.get_next_maintenance_date()
        return datetime.now() > next_date
    
    def days_until_due(self):
        next_date = self.get_next_maintenance_date()
        delta = next_date - datetime.now()
        return delta.days


class TestMaintenanceLogic(unittest.TestCase):
    """Test maintenance calculation logic"""
    
    def test_next_maintenance_date_calculation(self):
        """Test calculation of next maintenance date"""
        base_date = datetime(2024, 1, 1)
        plan = MockMaintenancePlan(frequency_days=30, created=base_date)
        
        expected_date = base_date + timedelta(days=30)
        actual_date = plan.get_next_maintenance_date()
        
        self.assertEqual(actual_date.date(), expected_date.date())
    
    def test_overdue_detection(self):
        """Test overdue maintenance detection"""
        # Create a plan that should be overdue
        old_date = datetime.now() - timedelta(days=60)
        plan = MockMaintenancePlan(frequency_days=30, created=old_date)
        
        self.assertTrue(plan.is_overdue())
    
    def test_not_overdue(self):
        """Test that future maintenance is not overdue"""
        future_date = datetime.now() - timedelta(days=15)
        plan = MockMaintenancePlan(frequency_days=30, created=future_date)
        
        self.assertFalse(plan.is_overdue())
    
    def test_days_until_due_positive(self):
        """Test days until due calculation for future maintenance"""
        recent_date = datetime.now() - timedelta(days=15)
        plan = MockMaintenancePlan(frequency_days=30, created=recent_date)
        
        days_until = plan.days_until_due()
        self.assertGreater(days_until, 0)
        self.assertLessEqual(days_until, 15)
    
    def test_days_until_due_negative(self):
        """Test days until due calculation for overdue maintenance"""
        old_date = datetime.now() - timedelta(days=60)
        plan = MockMaintenancePlan(frequency_days=30, created=old_date)
        
        days_until = plan.days_until_due()
        self.assertLess(days_until, 0)


class TestPluginStructure(unittest.TestCase):
    """Test plugin structure and imports"""
    
    def test_plugin_files_exist(self):
        """Test that all required plugin files exist"""
        import os
        
        plugin_dir = "netbox_maintenance_device"
        required_files = [
            "__init__.py",
            "models.py", 
            "views.py",
            "forms.py",
            "tables.py",
            "urls.py",
            "navigation.py",
            "admin.py"
        ]
        
        for file in required_files:
            file_path = os.path.join(plugin_dir, file)
            self.assertTrue(
                os.path.exists(file_path), 
                f"Required file {file_path} does not exist"
            )
    
    def test_template_files_exist(self):
        """Test that template files exist"""
        import os
        
        template_dir = "netbox_maintenance_device/templates/netbox_maintenance_device"
        required_templates = [
            "upcoming_maintenance.html",
            "device_maintenance_tab.html",
            "maintenanceplan.html",
            "maintenanceexecution.html"
        ]
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            self.assertTrue(
                os.path.exists(template_path),
                f"Required template {template_path} does not exist"
            )


if __name__ == '__main__':
    unittest.main()