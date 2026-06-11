import logging
from django.conf import settings
from django.utils.module_loading import import_string
from core.models import ObjectType
from extras.events import get_snapshots, serialize_for_event
from netbox.context import current_request, events_queue

logger = logging.getLogger('netbox.plugins.maintenance_device.events')


def fire_event(instance, event_type, request=None):
    """
    Fire a custom event for a MaintenancePlan or MaintenanceExecution.
    If inside a request context (Web UI, API request), it enqueues the event.
    Otherwise (e.g. management command, background worker), it flushes the event immediately.
    """
    if request is None:
        try:
            request = current_request.get()
        except LookupError:
            request = None

    # Try to get request's event queue
    queue = None
    if request is not None:
        try:
            queue = events_queue.get()
        except LookupError:
            pass

    user = getattr(request, 'user', None) if request else None
    username = user.username if user else 'system'
    request_id = getattr(request, 'id', None)

    event_data = {
        'object_type': ObjectType.objects.get_for_model(instance),
        'object_id': instance.pk,
        'object': instance,
        'event_type': event_type,
        # Event pipeline consumers (process_event_rules) read event['data']
        # unconditionally; NetBox 4.6's EventContext fills it lazily, but the
        # plain-dict path (NetBox <= 4.5 and the immediate-flush branch below)
        # must carry it eagerly or every matching event rule dies on KeyError.
        'data': serialize_for_event(instance),
        'snapshots': get_snapshots(instance, event_type),
        'request': request,
        'user': user,
        'username': username,
        'request_id': request_id,
    }

    if queue is not None:
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        # Use a key combining model and event type to prevent multiple events
        # from overwriting each other in the request queue dict.
        key = f'{app_label}.{model_name}:{instance.pk}:{event_type}'
        
        try:
            from extras.events import EventContext
            queue[key] = EventContext(**event_data)
        except ImportError:
            queue[key] = event_data
            
        logger.debug(f"Enqueued event '{event_type}' for {instance} in request queue")
    else:
        # Flush immediately for synchronous processing outside request cycle
        logger.info(f"Firing event '{event_type}' for {instance} immediately")
        for name in settings.EVENTS_PIPELINE:
            try:
                func = import_string(name)
                func([event_data])
            except Exception as e:
                logger.error(f"Error processing event pipeline {name}: {e}")
