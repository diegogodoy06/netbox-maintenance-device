"""
Permissions for the custom actions of the NetBox Maintenance Device API.

Standard CRUD routes use NetBox's default TokenPermissions. A custom permission
class replaces that default for the action it's applied to, so these must enforce
token write access themselves. They are only used on POST actions.
"""

from rest_framework import permissions

from users.models import Token


class _MaintenanceActionPermission(permissions.BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if isinstance(request.auth, Token) and not request.auth.write_enabled:
            return False
        return user.has_perm(self.required_permission)


class CanScheduleMaintenance(_MaintenanceActionPermission):
    """Permission to schedule maintenance executions"""
    required_permission = 'netbox_maintenance_device.add_maintenanceexecution'


class CanCompleteMaintenance(_MaintenanceActionPermission):
    """Permission to complete or cancel maintenance executions"""
    required_permission = 'netbox_maintenance_device.change_maintenanceexecution'
