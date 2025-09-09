from netbox.api.viewsets import NetBoxModelViewSet
from netbox_maintenance_device import models
from .serializers import MaintenancePlanSerializer, MaintenanceExecutionSerializer


class MaintenancePlanViewSet(NetBoxModelViewSet):
    queryset = models.MaintenancePlan.objects.prefetch_related('tags')
    serializer_class = MaintenancePlanSerializer


class MaintenanceExecutionViewSet(NetBoxModelViewSet):
    queryset = models.MaintenanceExecution.objects.prefetch_related('tags')
    serializer_class = MaintenanceExecutionSerializer
