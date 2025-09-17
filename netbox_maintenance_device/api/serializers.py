from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from netbox_maintenance_device import models
from django.utils import timezone


class DeviceNestedSerializer(WritableNestedSerializer):
    """Nested serializer for Device references - NetBox 4.4.x compatible"""
    
    class Meta:
        # Import Device model at class level
        from dcim import models as dcim_models
        model = dcim_models.Device
        fields = ['id', 'url', 'display', 'name']


class NestedMaintenancePlanSerializer(WritableNestedSerializer):
    """Nested serializer for MaintenancePlan references"""
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceplan-detail'
    )

    class Meta:
        model = models.MaintenancePlan
        fields = ['id', 'url', 'display', 'name', 'maintenance_type']


class NestedMaintenanceExecutionSerializer(WritableNestedSerializer):
    """Nested serializer for MaintenanceExecution references"""
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceexecution-detail'
    )

    class Meta:
        model = models.MaintenanceExecution
        fields = ['id', 'url', 'display', 'scheduled_date', 'status']


class MaintenancePlanSerializer(NetBoxModelSerializer):
    """Complete serializer for MaintenancePlan with all relationships and computed fields"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceplan-detail'
    )
    
    # Nested relationships
    device = DeviceNestedSerializer()
    executions = NestedMaintenanceExecutionSerializer(many=True, read_only=True)
    
    # Computed fields
    execution_count = serializers.IntegerField(read_only=True)
    next_maintenance_date = serializers.DateTimeField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    last_execution_date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = models.MaintenancePlan
        fields = [
            'id', 'url', 'display', 'device', 'name', 'description', 
            'maintenance_type', 'frequency_days', 'is_active',
            'created', 'last_updated', 'custom_field_data', 'tags',
            # Relationships
            'executions', 'execution_count',
            # Computed fields
            'next_maintenance_date', 'is_overdue', 'days_until_due',
            'last_execution_date'
        ]
        
    def validate_frequency_days(self, value):
        """Validate frequency days is positive and reasonable"""
        if value <= 0:
            raise serializers.ValidationError("Frequency must be greater than 0 days")
        if value > 3650:  # 10 years
            raise serializers.ValidationError("Frequency cannot exceed 3650 days (10 years)")
        return value
    
    def validate(self, data):
        """Additional model-level validations"""
        device = data.get('device')
        name = data.get('name')
        
        # Check for duplicate plan names per device (excluding current instance)
        if device and name:
            existing_plans = models.MaintenancePlan.objects.filter(
                device=device, name=name
            )
            if self.instance:
                existing_plans = existing_plans.exclude(pk=self.instance.pk)
            
            if existing_plans.exists():
                raise serializers.ValidationError({
                    'name': f"A maintenance plan with name '{name}' already exists for this device."
                })
        
        return data
    
    def to_representation(self, instance):
        """Add computed fields to the representation"""
        data = super().to_representation(instance)
        
        # Add computed fields
        data['execution_count'] = instance.executions.count()
        data['next_maintenance_date'] = instance.get_next_maintenance_date()
        data['is_overdue'] = instance.is_overdue()
        data['days_until_due'] = instance.days_until_due()
        
        # Add last execution date
        last_execution = instance.executions.filter(completed=True).order_by('-completed_date').first()
        data['last_execution_date'] = last_execution.completed_date if last_execution else None
        
        return data


class MaintenanceExecutionSerializer(NetBoxModelSerializer):
    """Complete serializer for MaintenanceExecution with all relationships and validations"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenance_device-api:maintenanceexecution-detail'
    )
    
    # Nested relationships
    maintenance_plan = NestedMaintenancePlanSerializer()
    
    # Computed fields
    device = serializers.CharField(source='maintenance_plan.device.name', read_only=True)
    device_id = serializers.IntegerField(source='maintenance_plan.device.id', read_only=True)
    plan_name = serializers.CharField(source='maintenance_plan.name', read_only=True)
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = models.MaintenanceExecution
        fields = [
            'id', 'url', 'display', 'maintenance_plan', 'scheduled_date', 
            'completed_date', 'status', 'notes', 'technician', 'completed',
            'created', 'last_updated', 'custom_field_data', 'tags',
            # Computed fields
            'device', 'device_id', 'plan_name', 'duration_days'
        ]
    
    def get_duration_days(self, obj):
        """Calculate duration between scheduled and completed dates"""
        if obj.scheduled_date and obj.completed_date:
            delta = obj.completed_date - obj.scheduled_date
            return delta.days
        return None
    
    def validate_scheduled_date(self, value):
        """Validate scheduled date is not too far in the past"""
        if value and value.date() < (timezone.now().date() - timezone.timedelta(days=365)):
            raise serializers.ValidationError("Scheduled date cannot be more than 1 year in the past")
        return value
    
    def validate_completed_date(self, value):
        """Validate completed date is not in the future"""
        if value and value.date() > timezone.now().date():
            raise serializers.ValidationError("Completed date cannot be in the future")
        return value
    
    def validate(self, data):
        """Additional model-level validations"""
        scheduled_date = data.get('scheduled_date')
        completed_date = data.get('completed_date')
        status = data.get('status')
        
        # If status is completed, completed_date should be set
        if status == 'completed' and not completed_date:
            raise serializers.ValidationError({
                'completed_date': "Completed date is required when status is 'completed'."
            })
        
        # If completed_date is set, status should be completed
        if completed_date and status != 'completed':
            raise serializers.ValidationError({
                'status': "Status must be 'completed' when completed date is set."
            })
        
        # Completed date should not be before scheduled date
        if scheduled_date and completed_date and completed_date < scheduled_date:
            raise serializers.ValidationError({
                'completed_date': "Completed date cannot be before scheduled date."
            })
        
        return data


# Bulk operation serializers for efficient operations
class BulkMaintenancePlanSerializer(serializers.ListSerializer):
    """Bulk operations for MaintenancePlan"""
    
    def create(self, validated_data):
        """Bulk create maintenance plans"""
        return [models.MaintenancePlan.objects.create(**attrs) for attrs in validated_data]
    
    def update(self, instance_list, validated_data):
        """Bulk update maintenance plans"""
        plan_mapping = {plan.id: plan for plan in instance_list}
        
        updated_plans = []
        for attrs in validated_data:
            plan_id = attrs.pop('id', None)
            if plan_id and plan_id in plan_mapping:
                plan = plan_mapping[plan_id]
                for key, value in attrs.items():
                    setattr(plan, key, value)
                plan.save()
                updated_plans.append(plan)
        
        return updated_plans


class BulkMaintenanceExecutionSerializer(serializers.ListSerializer):
    """Bulk operations for MaintenanceExecution"""
    
    def create(self, validated_data):
        """Bulk create maintenance executions"""
        return [models.MaintenanceExecution.objects.create(**attrs) for attrs in validated_data]
