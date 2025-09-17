"""
Custom permissions for NetBox Maintenance Device API.

This module defines custom permission classes for the API endpoints,
following NetBox patterns and ensuring proper access control.
"""

from rest_framework import permissions


class MaintenanceDevicePermissions(permissions.BasePermission):
    """
    Custom permissions for maintenance device operations.
    
    Provides granular control for maintenance device API operations
    with proper object-level permissions.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the requested action"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Map HTTP methods to permission requirements
        permission_map = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
        }
        
        required_action = permission_map.get(request.method, 'view')
        
        # Get the model name from the viewset
        if hasattr(view, 'queryset') and view.queryset is not None:
            model_name = view.queryset.model._meta.model_name
            perm_name = f'netbox_maintenance_device.{required_action}_{model_name}'
            return request.user.has_perm(perm_name)
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        return self.has_permission(request, view)


class CanScheduleMaintenance(permissions.BasePermission):
    """Permission to schedule maintenance executions"""
    
    def has_permission(self, request, view):
        """Check if user has permission to schedule maintenance"""
        return (request.user and 
                request.user.is_authenticated and 
                request.user.has_perm('netbox_maintenance_device.add_maintenanceexecution'))


class CanCompleteMaintenance(permissions.BasePermission):
    """Permission to complete maintenance executions"""
    
    def has_permission(self, request, view):
        """Check if user has permission to complete maintenance"""
        return (request.user and 
                request.user.is_authenticated and 
                request.user.has_perm('netbox_maintenance_device.change_maintenanceexecution'))