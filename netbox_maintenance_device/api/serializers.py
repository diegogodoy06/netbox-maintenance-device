from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from netbox_maintenance_device import models


class MaintenancePlanSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceplan-detail'
    )

    class Meta:
        model = models.MaintenancePlan
        fields = [
            'id', 'url', 'display', 'device', 'name', 'description', 
            'maintenance_type', 'frequency_days', 'last_executed', 
            'is_active', 'created', 'last_updated', 'custom_field_data', 'tags'
        ]


class MaintenanceExecutionSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceexecution-detail'
    )

    class Meta:
        model = models.MaintenanceExecution
        fields = [
            'id', 'url', 'display', 'maintenance_plan', 'scheduled_date', 
            'completed_date', 'status', 'notes', 'technician', 'completed',
            'created', 'last_updated', 'custom_field_data', 'tags'
        ]
