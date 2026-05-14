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


class VirtualMachineNestedSerializer(WritableNestedSerializer):
    """Nested serializer for VirtualMachine references."""

    class Meta:
        from virtualization import models as virt_models
        model = virt_models.VirtualMachine
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
    device = DeviceNestedSerializer(required=False, allow_null=True)
    virtual_machine = VirtualMachineNestedSerializer(required=False, allow_null=True)
    executions = NestedMaintenanceExecutionSerializer(many=True, read_only=True)

    # Computed fields
    execution_count = serializers.IntegerField(read_only=True)
    next_maintenance_date = serializers.DateTimeField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    last_execution_date = serializers.DateTimeField(read_only=True)
    target_type = serializers.CharField(read_only=True)

    class Meta:
        model = models.MaintenancePlan
        fields = [
            'id', 'url', 'display', 'device', 'virtual_machine', 'name', 'description',
            'maintenance_type', 'frequency_days', 'frequency_unit', 'anchor_date',
            'is_active',
            'created', 'last_updated', 'custom_field_data', 'tags',
            # Relationships
            'executions', 'execution_count',
            # Computed fields
            'next_maintenance_date', 'is_overdue', 'days_until_due',
            'last_execution_date', 'target_type',
        ]

    def validate_frequency_days(self, value):
        """Validate frequency count is positive."""
        if value is None or value <= 0:
            raise serializers.ValidationError("Frequency must be greater than 0")
        return value

    def validate(self, data):
        """Cross-field validation: exactly one target, unique name per target."""
        # `data` carries only the fields submitted; merge with instance for partial updates.
        device = data.get('device', getattr(self.instance, 'device', None))
        vm = data.get('virtual_machine', getattr(self.instance, 'virtual_machine', None))
        name = data.get('name', getattr(self.instance, 'name', None))

        if device and vm:
            raise serializers.ValidationError(
                "Pick either a device or a virtual machine, not both."
            )
        if not device and not vm:
            raise serializers.ValidationError(
                "A maintenance plan must reference either a device or a virtual machine."
            )

        if name:
            target_filter = {'device': device} if device else {'virtual_machine': vm}
            existing_plans = models.MaintenancePlan.objects.filter(name=name, **target_filter)
            if self.instance:
                existing_plans = existing_plans.exclude(pk=self.instance.pk)

            if existing_plans.exists():
                target_label = 'device' if device else 'virtual machine'
                raise serializers.ValidationError({
                    'name': (
                        f"A maintenance plan with name '{name}' already exists "
                        f"for this {target_label}."
                    )
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
        data['target_type'] = instance.target_type

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
    
    # Computed fields — kept for backward compatibility with existing API consumers.
    device = serializers.CharField(source='maintenance_plan.device.name', read_only=True, default=None)
    device_id = serializers.IntegerField(source='maintenance_plan.device.id', read_only=True, default=None)
    virtual_machine = serializers.CharField(
        source='maintenance_plan.virtual_machine.name', read_only=True, default=None,
    )
    virtual_machine_id = serializers.IntegerField(
        source='maintenance_plan.virtual_machine.id', read_only=True, default=None,
    )
    target_type = serializers.CharField(source='maintenance_plan.target_type', read_only=True)
    plan_name = serializers.CharField(source='maintenance_plan.name', read_only=True)
    duration_days = serializers.SerializerMethodField()

    class Meta:
        model = models.MaintenanceExecution
        fields = [
            'id', 'url', 'display', 'maintenance_plan', 'scheduled_date',
            'completed_date', 'status', 'notes', 'technician', 'completed',
            'created', 'last_updated', 'custom_field_data', 'tags',
            # Computed fields
            'device', 'device_id', 'virtual_machine', 'virtual_machine_id',
            'target_type', 'plan_name', 'duration_days',
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
