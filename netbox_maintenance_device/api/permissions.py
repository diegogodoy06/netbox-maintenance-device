"""
Custom permissions for NetBox Maintenance Device API.

This module defines custom permission classes for the API endpoints,
following NetBox patterns and ensuring proper access control.
"""

from rest_framework import permissions
from netbox.api.authentication import TokenPermissions


class MaintenanceDevicePermissions(TokenPermissions):
    """
    Custom permissions for maintenance device operations.
    
    Extends NetBox's TokenPermissions to provide granular control
    over maintenance operations based on user roles and permissions.
    """
    
    # Permission mapping for different actions
    perms_map = {
        'GET': [],  # Read permissions (handled by NetBox)
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['netbox_maintenance_device.add_maintenanceplan', 'netbox_maintenance_device.add_maintenanceexecution'],
        'PUT': ['netbox_maintenance_device.change_maintenanceplan', 'netbox_maintenance_device.change_maintenanceexecution'],
        'PATCH': ['netbox_maintenance_device.change_maintenanceplan', 'netbox_maintenance_device.change_maintenanceexecution'],
        'DELETE': ['netbox_maintenance_device.delete_maintenanceplan', 'netbox_maintenance_device.delete_maintenanceexecution'],
    }


class CanScheduleMaintenance(permissions.BasePermission):
    """
    Custom permission to check if user can schedule maintenance executions.
    
    This could be used for the schedule_maintenance custom action.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to schedule maintenance"""
        return request.user.has_perm('netbox_maintenance_device.add_maintenanceexecution')
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission for scheduling"""
        # Only allow scheduling if the plan is active
        if hasattr(obj, 'is_active'):
            return obj.is_active and request.user.has_perm('netbox_maintenance_device.add_maintenanceexecution')
        return request.user.has_perm('netbox_maintenance_device.add_maintenanceexecution')


class CanCompleteMaintenance(permissions.BasePermission):
    """
    Custom permission to check if user can complete maintenance executions.
    
    This could be used for the complete custom action.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to complete maintenance"""
        return request.user.has_perm('netbox_maintenance_device.change_maintenanceexecution')
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission for completion"""
        # Only allow completion if execution is not already completed
        if hasattr(obj, 'status'):
            return obj.status != 'completed' and request.user.has_perm('netbox_maintenance_device.change_maintenanceexecution')
        return request.user.has_perm('netbox_maintenance_device.change_maintenanceexecution')


class ReadOnlyOrAuthenticatedWrite(permissions.BasePermission):
    """
    Custom permission to allow read access to anyone but write access only to authenticated users.
    
    This might be useful for public read access to maintenance schedules while restricting writes.
    """
    
    def has_permission(self, request, view):
        """Check permission based on request method"""
        if request.method in permissions.SAFE_METHODS:
            # Allow read access to authenticated users or with valid API token
            return request.user and (request.user.is_authenticated or hasattr(request, 'auth'))
        
        # Write operations require authentication and appropriate permissions
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.has_perm(f'netbox_maintenance_device.add_{view.queryset.model._meta.model_name}')
        )


class DeviceOwnerPermission(permissions.BasePermission):
    """
    Permission class to restrict maintenance operations based on device ownership or assignment.
    
    This could be used if you want to restrict users to only manage maintenance
    for devices they are responsible for.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for this specific device's maintenance"""
        # Get the device from the object
        device = None
        if hasattr(obj, 'device'):
            device = obj.device
        elif hasattr(obj, 'maintenance_plan'):
            device = obj.maintenance_plan.device
        
        if not device:
            return True  # Allow if we can't determine device
        
        # If device has a primary_user field or similar, check against it
        # This is an example - adjust based on your device model structure
        if hasattr(device, 'primary_user') and device.primary_user:
            return device.primary_user == request.user
        
        # If device is assigned to a tenant and user belongs to that tenant
        if hasattr(device, 'tenant') and device.tenant:
            if hasattr(request.user, 'tenant') and request.user.tenant:
                return device.tenant == request.user.tenant
        
        # Default to allowing access if no specific ownership rules apply
        return True


# Permission classes that can be used in ViewSets
class MaintenancePlanPermissions(MaintenanceDevicePermissions):
    """Specific permissions for MaintenancePlan operations"""
    
    def has_permission(self, request, view):
        """Custom permission logic for maintenance plans"""
        # Call parent permission check first
        if not super().has_permission(request, view):
            return False
        
        # Add any specific business logic for maintenance plans
        # For example, check if user can access maintenance features
        if not request.user.has_perm('netbox_maintenance_device.view_maintenanceplan'):
            return False
        
        return True


class MaintenanceExecutionPermissions(MaintenanceDevicePermissions):
    """Specific permissions for MaintenanceExecution operations"""
    
    def has_permission(self, request, view):
        """Custom permission logic for maintenance executions"""
        # Call parent permission check first
        if not super().has_permission(request, view):
            return False
        
        # Add any specific business logic for maintenance executions
        if not request.user.has_perm('netbox_maintenance_device.view_maintenanceexecution'):
            return False
        
        return True


# Convenience function to get appropriate permission classes
def get_maintenance_permissions():
    """
    Return the default permission classes for maintenance API endpoints.
    
    This function can be imported and used in ViewSets to ensure
    consistent permission handling across all endpoints.
    """
    return [MaintenanceDevicePermissions]


def get_action_permissions(action_name):
    """
    Return permission classes for specific custom actions.
    
    Args:
        action_name (str): Name of the custom action
    
    Returns:
        list: List of permission classes for the action
    """
    action_permissions = {
        'schedule_maintenance': [CanScheduleMaintenance],
        'complete': [CanCompleteMaintenance],
        'cancel': [CanCompleteMaintenance],  # Same permissions as complete
        'statistics': [],  # Allow for authenticated users (handled by ViewSet)
        'overdue': [],
        'upcoming': [],
        'pending': [],
        'overdue_executions': [],
    }
    
    return action_permissions.get(action_name, [MaintenanceDevicePermissions])