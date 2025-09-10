from django.urls import path
from . import views, models

app_name = 'netbox_maintenance_device'

urlpatterns = [
    # Maintenance Plans
    path('maintenance-plans/', views.MaintenancePlanListView.as_view(), name='maintenanceplan_list'),
    path('maintenance-plans/add/', views.MaintenancePlanEditView.as_view(), name='maintenanceplan_add'),
    path('maintenance-plans/<int:pk>/', views.MaintenancePlanView.as_view(), name='maintenanceplan'),
    path('maintenance-plans/<int:pk>/edit/', views.MaintenancePlanEditView.as_view(), name='maintenanceplan_edit'),
    path('maintenance-plans/<int:pk>/delete/', views.MaintenancePlanDeleteView.as_view(), name='maintenanceplan_delete'),
    path('maintenance-plans/<int:pk>/changelog/', views.MaintenancePlanChangeLogView.as_view(), name='maintenanceplan_changelog', kwargs={'model': models.MaintenancePlan}),
    
    # Maintenance Executions
    path('maintenance-executions/', views.MaintenanceExecutionListView.as_view(), name='maintenanceexecution_list'),
    path('maintenance-executions/add/', views.MaintenanceExecutionEditView.as_view(), name='maintenanceexecution_add'),
    path('maintenance-executions/<int:pk>/', views.MaintenanceExecutionView.as_view(), name='maintenanceexecution'),
    path('maintenance-executions/<int:pk>/edit/', views.MaintenanceExecutionEditView.as_view(), name='maintenanceexecution_edit'),
    path('maintenance-executions/<int:pk>/delete/', views.MaintenanceExecutionDeleteView.as_view(), name='maintenanceexecution_delete'),
    path('maintenance-executions/<int:pk>/changelog/', views.MaintenanceExecutionChangeLogView.as_view(), name='maintenanceexecution_changelog', kwargs={'model': models.MaintenanceExecution}),
    
    # Dashboard
    path('upcoming/', views.UpcomingMaintenanceView.as_view(), name='upcoming_maintenance'),
    
    # Device Tab
    path('device/<int:pk>/maintenance/', views.device_maintenance_tab, name='device_maintenance_tab'),
    
    # Quick Actions
    path('quick-complete/', views.quick_complete_maintenance, name='quick_complete'),
    path('schedule/', views.schedule_maintenance, name='schedule_maintenance'),
]