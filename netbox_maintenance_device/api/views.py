from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from netbox.api.viewsets import NetBoxModelViewSet
from netbox.api.pagination import OptionalLimitOffsetPagination

from netbox_maintenance_device import models
from .serializers import (
    MaintenancePlanSerializer, 
    MaintenanceExecutionSerializer,
    NestedMaintenancePlanSerializer,
    NestedMaintenanceExecutionSerializer
)
from .permissions import (
    MaintenanceDevicePermissions,
    CanScheduleMaintenance,
    CanCompleteMaintenance
)


class MaintenancePlanFilter(filters.FilterSet):
    """Advanced filtering for MaintenancePlan API"""
    
    # Device filters
    device_id = filters.ModelMultipleChoiceFilter(
        field_name='device',
        queryset=lambda request: models.Device.objects.all(),
        label='Device (ID)',
    )
    device = filters.CharFilter(
        field_name='device__name',
        lookup_expr='icontains',
        label='Device (name)',
    )
    
    # Maintenance type filters
    maintenance_type = filters.MultipleChoiceFilter(
        choices=models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES,
        label='Maintenance Type',
    )
    
    # Frequency filters
    frequency_days = filters.NumberFilter(
        field_name='frequency_days',
        label='Exact frequency (days)',
    )
    frequency_days__gte = filters.NumberFilter(
        field_name='frequency_days',
        lookup_expr='gte',
        label='Minimum frequency (days)',
    )
    frequency_days__lte = filters.NumberFilter(
        field_name='frequency_days',
        lookup_expr='lte',
        label='Maximum frequency (days)',
    )
    
    # Status filters
    is_active = filters.BooleanFilter(
        field_name='is_active',
        label='Active status',
    )
    
    # Date filters
    created = filters.DateFilter(
        field_name='created__date',
        label='Created date',
    )
    created__gte = filters.DateFilter(
        field_name='created__date',
        lookup_expr='gte',
        label='Created after',
    )
    created__lte = filters.DateFilter(
        field_name='created__date',
        lookup_expr='lte',
        label='Created before',
    )
    
    # Text search
    q = filters.CharFilter(
        method='search',
        label='Search',
    )
    
    def search(self, queryset, name, value):
        """Full-text search across multiple fields"""
        if not value.strip():
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(device__name__icontains=value) |
            Q(device__serial__icontains=value)
        ).distinct()
    
    class Meta:
        model = models.MaintenancePlan
        fields = []


class MaintenanceExecutionFilter(filters.FilterSet):
    """Advanced filtering for MaintenanceExecution API"""
    
    # Plan filters
    maintenance_plan_id = filters.ModelMultipleChoiceFilter(
        field_name='maintenance_plan',
        queryset=lambda request: models.MaintenancePlan.objects.all(),
        label='Maintenance Plan (ID)',
    )
    maintenance_plan = filters.CharFilter(
        field_name='maintenance_plan__name',
        lookup_expr='icontains',
        label='Maintenance Plan (name)',
    )
    
    # Device filters (through plan)
    device_id = filters.ModelMultipleChoiceFilter(
        field_name='maintenance_plan__device',
        queryset=lambda request: models.Device.objects.all(),
        label='Device (ID)',
    )
    device = filters.CharFilter(
        field_name='maintenance_plan__device__name',
        lookup_expr='icontains',
        label='Device (name)',
    )
    
    # Status filters
    status = filters.MultipleChoiceFilter(
        choices=models.MaintenanceExecution.STATUS_CHOICES,
        label='Status',
    )
    completed = filters.BooleanFilter(
        field_name='completed',
        label='Completed',
    )
    
    # Date filters
    scheduled_date = filters.DateFilter(
        field_name='scheduled_date__date',
        label='Scheduled date',
    )
    scheduled_date__gte = filters.DateFilter(
        field_name='scheduled_date__date',
        lookup_expr='gte',
        label='Scheduled after',
    )
    scheduled_date__lte = filters.DateFilter(
        field_name='scheduled_date__date',
        lookup_expr='lte',
        label='Scheduled before',
    )
    
    completed_date = filters.DateFilter(
        field_name='completed_date__date',
        label='Completed date',
    )
    completed_date__gte = filters.DateFilter(
        field_name='completed_date__date',
        lookup_expr='gte',
        label='Completed after',
    )
    completed_date__lte = filters.DateFilter(
        field_name='completed_date__date',
        lookup_expr='lte',
        label='Completed before',
    )
    
    # Technician filter
    technician = filters.CharFilter(
        field_name='technician',
        lookup_expr='icontains',
        label='Technician',
    )
    
    # Text search
    q = filters.CharFilter(
        method='search',
        label='Search',
    )
    
    def search(self, queryset, name, value):
        """Full-text search across multiple fields"""
        if not value.strip():
            return queryset
        
        return queryset.filter(
            Q(maintenance_plan__name__icontains=value) |
            Q(maintenance_plan__device__name__icontains=value) |
            Q(notes__icontains=value) |
            Q(technician__icontains=value)
        ).distinct()
    
    class Meta:
        model = models.MaintenanceExecution
        fields = []


class MaintenancePlanViewSet(NetBoxModelViewSet):
    """Complete API ViewSet for MaintenancePlan with advanced features"""
    
    queryset = models.MaintenancePlan.objects.select_related('device').prefetch_related(
        'tags',
        Prefetch('executions', queryset=models.MaintenanceExecution.objects.order_by('-scheduled_date'))
    )
    serializer_class = MaintenancePlanSerializer
    filterset_class = MaintenancePlanFilter
    permission_classes = [MaintenanceDevicePermissions]
    
    # Ordering options
    ordering_fields = [
        'id', 'name', 'device__name', 'maintenance_type', 
        'frequency_days', 'is_active', 'created', 'last_updated'
    ]
    ordering = ['device__name', 'name']
    
    # Search fields for basic search
    search_fields = ['name', 'description', 'device__name', 'device__serial']
    
    def get_queryset(self):
        """Optimize queryset with annotations for computed fields"""
        queryset = super().get_queryset()
        
        # Add execution count annotation
        queryset = queryset.annotate(
            execution_count=Count('executions')
        )
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[CanScheduleMaintenance])
    def schedule_maintenance(self, request, pk=None):
        """Custom action to schedule a new maintenance execution"""
        plan = self.get_object()
        
        # Get data from request
        scheduled_date = request.data.get('scheduled_date')
        notes = request.data.get('notes', '')
        technician = request.data.get('technician', '')
        
        if not scheduled_date:
            return Response(
                {'error': 'scheduled_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new execution
        execution = models.MaintenanceExecution.objects.create(
            maintenance_plan=plan,
            scheduled_date=scheduled_date,
            notes=notes,
            technician=technician,
            status='scheduled'
        )
        
        serializer = NestedMaintenanceExecutionSerializer(execution, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue maintenance plans"""
        overdue_plans = []
        
        for plan in self.get_queryset():
            if plan.is_overdue():
                overdue_plans.append(plan)
        
        page = self.paginate_queryset(overdue_plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get maintenance plans due within specified days (default: 30)"""
        days = int(request.query_params.get('days', 30))
        upcoming_plans = []
        
        for plan in self.get_queryset():
            days_until = plan.days_until_due()
            if days_until is not None and 0 <= days_until <= days:
                upcoming_plans.append(plan)
        
        page = self.paginate_queryset(upcoming_plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming_plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get maintenance plan statistics"""
        queryset = self.get_queryset()
        
        total_plans = queryset.count()
        active_plans = queryset.filter(is_active=True).count()
        inactive_plans = total_plans - active_plans
        
        # Count by maintenance type
        preventive_count = queryset.filter(maintenance_type='preventive').count()
        corrective_count = queryset.filter(maintenance_type='corrective').count()
        
        # Count overdue plans
        overdue_count = sum(1 for plan in queryset if plan.is_overdue())
        
        return Response({
            'total_plans': total_plans,
            'active_plans': active_plans,
            'inactive_plans': inactive_plans,
            'preventive_plans': preventive_count,
            'corrective_plans': corrective_count,
            'overdue_plans': overdue_count,
        })


class MaintenanceExecutionViewSet(NetBoxModelViewSet):
    """Complete API ViewSet for MaintenanceExecution with advanced features"""
    
    queryset = models.MaintenanceExecution.objects.select_related(
        'maintenance_plan',
        'maintenance_plan__device'
    ).prefetch_related('tags')
    serializer_class = MaintenanceExecutionSerializer
    filterset_class = MaintenanceExecutionFilter
    permission_classes = [MaintenanceDevicePermissions]
    
    # Ordering options
    ordering_fields = [
        'id', 'scheduled_date', 'completed_date', 'status', 
        'maintenance_plan__name', 'maintenance_plan__device__name',
        'technician', 'created', 'last_updated'
    ]
    ordering = ['-scheduled_date']
    
    # Search fields for basic search
    search_fields = [
        'maintenance_plan__name', 'maintenance_plan__device__name',
        'notes', 'technician'
    ]
    
    @action(detail=True, methods=['post'], permission_classes=[CanCompleteMaintenance])
    def complete(self, request, pk=None):
        """Custom action to mark execution as completed"""
        execution = self.get_object()
        
        if execution.status == 'completed':
            return Response(
                {'error': 'Execution is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update execution
        execution.status = 'completed'
        execution.completed_date = timezone.now()
        execution.completed = True
        
        # Get additional data from request
        notes = request.data.get('notes')
        if notes:
            execution.notes = notes
        
        technician = request.data.get('technician')
        if technician:
            execution.technician = technician
        
        execution.save()
        
        serializer = self.get_serializer(execution)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[CanCompleteMaintenance])
    def cancel(self, request, pk=None):
        """Custom action to cancel execution"""
        execution = self.get_object()
        
        if execution.status == 'completed':
            return Response(
                {'error': 'Cannot cancel completed execution'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        execution.status = 'cancelled'
        
        # Get cancellation reason from request
        notes = request.data.get('notes')
        if notes:
            execution.notes = notes
        
        execution.save()
        
        serializer = self.get_serializer(execution)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending executions (scheduled or in_progress)"""
        pending_executions = self.get_queryset().filter(
            status__in=['scheduled', 'in_progress']
        )
        
        page = self.paginate_queryset(pending_executions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(pending_executions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_executions(self, request):
        """Get executions that are overdue (scheduled date has passed but not completed)"""
        overdue_executions = self.get_queryset().filter(
            scheduled_date__lt=timezone.now(),
            status__in=['scheduled', 'in_progress']
        )
        
        page = self.paginate_queryset(overdue_executions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_executions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get execution statistics"""
        queryset = self.get_queryset()
        
        total_executions = queryset.count()
        completed_executions = queryset.filter(status='completed').count()
        scheduled_executions = queryset.filter(status='scheduled').count()
        in_progress_executions = queryset.filter(status='in_progress').count()
        cancelled_executions = queryset.filter(status='cancelled').count()
        
        # Overdue executions
        overdue_executions = queryset.filter(
            scheduled_date__lt=timezone.now(),
            status__in=['scheduled', 'in_progress']
        ).count()
        
        return Response({
            'total_executions': total_executions,
            'completed_executions': completed_executions,
            'scheduled_executions': scheduled_executions,
            'in_progress_executions': in_progress_executions,
            'cancelled_executions': cancelled_executions,
            'overdue_executions': overdue_executions,
        })
