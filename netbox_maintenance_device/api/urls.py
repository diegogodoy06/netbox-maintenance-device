from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_maintenance_device-api'

router = NetBoxRouter()
router.register('maintenance-plans', views.MaintenancePlanViewSet)
router.register('maintenance-executions', views.MaintenanceExecutionViewSet)

urlpatterns = router.urls
