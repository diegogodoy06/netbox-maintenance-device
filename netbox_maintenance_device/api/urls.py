from django.urls import path, include
from netbox.api.routers import NetBoxRouter
from . import views

app_name = 'netbox_maintenance_device-api'

# Main API router for CRUD operations
router = NetBoxRouter()

# Register main viewsets
router.register('maintenance-plans', views.MaintenancePlanViewSet, basename='maintenanceplan')
router.register('maintenance-executions', views.MaintenanceExecutionViewSet, basename='maintenanceexecution')

# Include all router URLs
urlpatterns = [
    # Main API routes (includes all CRUD operations and custom actions)
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here if needed
    # Example: path('reports/', views.MaintenanceReportView.as_view(), name='maintenance-reports'),
]

# URL patterns summary for documentation:
# 
# MaintenancePlan endpoints:
# GET    /api/plugins/netbox-maintenance-device/maintenance-plans/           - List all plans
# POST   /api/plugins/netbox-maintenance-device/maintenance-plans/           - Create new plan
# GET    /api/plugins/netbox-maintenance-device/maintenance-plans/{id}/      - Get specific plan
# PUT    /api/plugins/netbox-maintenance-device/maintenance-plans/{id}/      - Update plan (full)
# PATCH  /api/plugins/netbox-maintenance-device/maintenance-plans/{id}/      - Update plan (partial)
# DELETE /api/plugins/netbox-maintenance-device/maintenance-plans/{id}/      - Delete plan
# 
# Custom MaintenancePlan actions:
# POST   /api/plugins/netbox-maintenance-device/maintenance-plans/{id}/schedule-maintenance/  - Schedule execution
# GET    /api/plugins/netbox-maintenance-device/maintenance-plans/overdue/                    - Get overdue plans
# GET    /api/plugins/netbox-maintenance-device/maintenance-plans/upcoming/                   - Get upcoming plans
# GET    /api/plugins/netbox-maintenance-device/maintenance-plans/statistics/                 - Get plan statistics
# 
# MaintenanceExecution endpoints:
# GET    /api/plugins/netbox-maintenance-device/maintenance-executions/      - List all executions
# POST   /api/plugins/netbox-maintenance-device/maintenance-executions/      - Create new execution
# GET    /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/ - Get specific execution
# PUT    /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/ - Update execution (full)
# PATCH  /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/ - Update execution (partial)
# DELETE /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/ - Delete execution
# 
# Custom MaintenanceExecution actions:
# POST   /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/complete/         - Mark as completed
# POST   /api/plugins/netbox-maintenance-device/maintenance-executions/{id}/cancel/           - Cancel execution
# GET    /api/plugins/netbox-maintenance-device/maintenance-executions/pending/               - Get pending executions
# GET    /api/plugins/netbox-maintenance-device/maintenance-executions/overdue-executions/    - Get overdue executions
# GET    /api/plugins/netbox-maintenance-device/maintenance-executions/statistics/            - Get execution statistics
#
# All endpoints support:
# - Filtering via query parameters (see FilterSets in views.py)
# - Ordering via ?ordering=field_name
# - Search via ?q=search_term
# - Pagination via ?limit=N&offset=N
# - Field selection via ?fields=field1,field2
# - Format selection via ?format=json|api (HTML browsable API)
