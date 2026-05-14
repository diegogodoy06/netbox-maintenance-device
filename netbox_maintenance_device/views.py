from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
from netbox.views import generic
from dcim.models import Device
from virtualization.models import VirtualMachine
from . import forms, models, tables


class MaintenancePlanListView(generic.ObjectListView):
    queryset = models.MaintenancePlan.objects.all()
    table = tables.MaintenancePlanTable
    filterset = forms.MaintenancePlanFilterSet


class MaintenancePlanView(generic.ObjectView):
    queryset = models.MaintenancePlan.objects.all()


class MaintenancePlanEditView(generic.ObjectEditView):
    queryset = models.MaintenancePlan.objects.all()
    form = forms.MaintenancePlanForm


class MaintenancePlanDeleteView(generic.ObjectDeleteView):
    queryset = models.MaintenancePlan.objects.all()


class MaintenancePlanChangeLogView(generic.ObjectChangeLogView):
    queryset = models.MaintenancePlan.objects.all()


class MaintenanceExecutionListView(generic.ObjectListView):
    queryset = models.MaintenanceExecution.objects.all()
    table = tables.MaintenanceExecutionTable
    filterset = forms.MaintenanceExecutionFilterSet


class MaintenanceExecutionView(generic.ObjectView):
    queryset = models.MaintenanceExecution.objects.all()


class MaintenanceExecutionEditView(generic.ObjectEditView):
    queryset = models.MaintenanceExecution.objects.all()
    form = forms.MaintenanceExecutionForm


class MaintenanceExecutionDeleteView(generic.ObjectDeleteView):
    queryset = models.MaintenanceExecution.objects.all()


class MaintenanceExecutionChangeLogView(generic.ObjectChangeLogView):
    queryset = models.MaintenanceExecution.objects.all()


UPCOMING_STATUS_CHOICES = [
    ('overdue', _('Overdue')),
    ('due_soon', _('Due Soon (≤ 7 days)')),
    ('upcoming', _('Upcoming (8–30 days)')),
    ('on_track', _('On Track (> 30 days)')),
]


def _classify_plan(days):
    """Map days-until-due to a status bucket used by the upcoming view filter."""
    if days is None:
        return None
    if days < 0:
        return 'overdue'
    if days <= 7:
        return 'due_soon'
    if days <= 30:
        return 'upcoming'
    return 'on_track'


class UpcomingMaintenanceView(generic.ObjectListView):
    """View for upcoming and overdue maintenance."""
    queryset = models.MaintenancePlan.objects.filter(is_active=True)
    table = tables.UpcomingMaintenanceTable
    template_name = 'netbox_maintenance_device/upcoming_maintenance.html'

    def _base_queryset(self, request):
        return (
            models.MaintenancePlan.objects.filter(is_active=True)
            .select_related('device', 'virtual_machine')
            .prefetch_related('executions')
        )

    def get_queryset(self, request):
        # Status, maintenance_type and target_type filters are applied here because
        # the status comes from a Python computation (next-due across units and
        # optional anchors) that can't be expressed as a single SQL predicate.
        qs = self._base_queryset(request)

        maintenance_type = request.GET.get('maintenance_type')
        if maintenance_type in {choice for choice, _label in models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES}:
            qs = qs.filter(maintenance_type=maintenance_type)

        target_type = request.GET.get('target_type')
        if target_type == 'device':
            qs = qs.filter(device__isnull=False)
        elif target_type == 'virtualmachine':
            qs = qs.filter(virtual_machine__isnull=False)

        status_filter = request.GET.get('status')
        if status_filter in {key for key, _label in UPCOMING_STATUS_CHOICES}:
            matching_pks = [
                plan.pk for plan in qs
                if _classify_plan(plan.days_until_due()) == status_filter
            ]
            qs = qs.filter(pk__in=matching_pks)

        return qs

    def get_extra_context(self, request):
        context = super().get_extra_context(request)

        # Stats use the unfiltered base set so badges always reflect the whole picture,
        # not the slice the user is currently viewing.
        overdue_count = due_soon_count = upcoming_count = on_track_count = 0
        for plan in self._base_queryset(request):
            bucket = _classify_plan(plan.days_until_due())
            if bucket == 'overdue':
                overdue_count += 1
            elif bucket == 'due_soon':
                due_soon_count += 1
            elif bucket == 'upcoming':
                upcoming_count += 1
            elif bucket == 'on_track':
                on_track_count += 1

        context.update({
            'overdue_count': overdue_count,
            'due_soon_count': due_soon_count,
            'upcoming_count': upcoming_count,
            'on_track_count': on_track_count,
            'total_plans': overdue_count + due_soon_count + upcoming_count + on_track_count,
            'status_choices': UPCOMING_STATUS_CHOICES,
            'maintenance_type_choices': models.MaintenancePlan.MAINTENANCE_TYPE_CHOICES,
            'selected_status': request.GET.get('status', ''),
            'selected_maintenance_type': request.GET.get('maintenance_type', ''),
            'selected_target_type': request.GET.get('target_type', ''),
        })
        return context


def device_maintenance_tab(request, pk):
    """Tab view for device maintenance history"""
    device = get_object_or_404(Device, pk=pk)
    maintenance_plans = models.MaintenancePlan.objects.filter(device=device).order_by('name')
    recent_executions = models.MaintenanceExecution.objects.filter(
        maintenance_plan__device=device
    ).order_by('-scheduled_date')[:10]

    # Count overdue maintenance
    overdue_count = sum(1 for plan in maintenance_plans if plan.is_overdue())

    context = {
        'target': device,
        'target_kind': 'device',
        'target_kwarg': 'device',
        'device': device,
        'object': device,  # For consistency with NetBox templates
        'maintenance_plans': maintenance_plans,
        'recent_executions': recent_executions,
        'overdue_count': overdue_count,
    }

    return render(request, 'netbox_maintenance_device/device_maintenance_tab.html', context)


def virtualmachine_maintenance_tab(request, pk):
    """Tab view for virtual machine maintenance history."""
    vm = get_object_or_404(VirtualMachine, pk=pk)
    maintenance_plans = models.MaintenancePlan.objects.filter(virtual_machine=vm).order_by('name')
    recent_executions = models.MaintenanceExecution.objects.filter(
        maintenance_plan__virtual_machine=vm
    ).order_by('-scheduled_date')[:10]

    overdue_count = sum(1 for plan in maintenance_plans if plan.is_overdue())

    context = {
        'target': vm,
        'target_kind': 'virtualmachine',
        'target_kwarg': 'virtual_machine',
        'device': vm,  # Templates reuse the 'device' name for the target object.
        'object': vm,
        'maintenance_plans': maintenance_plans,
        'recent_executions': recent_executions,
        'overdue_count': overdue_count,
    }

    return render(request, 'netbox_maintenance_device/device_maintenance_tab.html', context)


@require_http_methods(["POST"])
def quick_complete_maintenance(request):
    """Quick completion of maintenance via AJAX"""
    try:
        execution_id = request.POST.get('execution_id')
        plan_id = request.POST.get('plan_id')
        device_id = request.POST.get('device_id')
        technician = request.POST.get('technician', '')
        notes = request.POST.get('notes', '')
        
        if execution_id:
            # Complete existing execution
            execution = get_object_or_404(models.MaintenanceExecution, pk=execution_id)
            execution.status = 'completed'
            execution.completed_date = timezone.now()
            execution.technician = technician
            if notes:
                execution.notes = notes
            execution.save()
            
            return JsonResponse({
                'success': True, 
                'message': str(_('Maintenance execution completed successfully'))
            })
            
        elif plan_id and device_id:
            # Create and complete new execution for the plan
            plan = get_object_or_404(models.MaintenancePlan, pk=plan_id)
            
            # Use logged user as technician if not provided
            if not technician and request.user.is_authenticated:
                technician = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            
            execution = models.MaintenanceExecution.objects.create(
                maintenance_plan=plan,
                scheduled_date=timezone.now(),
                completed_date=timezone.now(),
                status='completed',
                technician=technician,
                notes=notes or 'Completed via quick action'
            )
            
            return JsonResponse({
                'success': True, 
                'message': str(_('Maintenance scheduled and completed successfully'))
            })
        else:
            return JsonResponse({
                'success': False, 
                'error': str(_('Missing required parameters'))
            }, status=400)
            
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@require_http_methods(["POST"])
def schedule_maintenance(request):
    """Schedule maintenance for a plan"""
    try:
        plan_id = request.POST.get('plan_id')
        scheduled_date = request.POST.get('scheduled_date')
        technician = request.POST.get('technician', '')
        notes = request.POST.get('notes', '')
        
        if not plan_id:
            return JsonResponse({
                'success': False, 
                'error': str(_('Missing maintenance plan ID'))
            }, status=400)
        
        plan = get_object_or_404(models.MaintenancePlan, pk=plan_id)
        
        # Use logged user as technician if not provided
        if not technician and request.user.is_authenticated:
            technician = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        
        # Use provided date or next maintenance date
        if scheduled_date:
            from datetime import datetime
            scheduled_datetime = datetime.strptime(scheduled_date, '%Y-%m-%d')
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
        else:
            scheduled_datetime = plan.get_next_maintenance_date() or timezone.now()
        
        execution = models.MaintenanceExecution.objects.create(
            maintenance_plan=plan,
            scheduled_date=scheduled_datetime,
            status='scheduled',
            technician=technician,
            notes=notes  # Don't add default note
        )
        
        return JsonResponse({
            'success': True, 
            'message': str(_('Maintenance scheduled successfully')),
            'execution_id': execution.pk
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)