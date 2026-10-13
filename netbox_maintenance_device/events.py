import logging
from inspect import signature
from django.conf import settings
from django.utils.module_loading import import_string
from core.models import ObjectType
from extras.events import get_snapshots, process_event_rules, serialize_for_event
from netbox.context import current_request, events_queue

logger = logging.getLogger('netbox.plugins.maintenance_device.events')

# NetBox 4.4 passes individual arguments to the rule processor and requires
# event['request'], even without an HTTP request. Later processors accept the
# event mapping and copy a request whenever that key is present.
_LEGACY_EVENT_PIPELINE = 'event_type' in signature(process_event_rules).parameters


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
    # The legacy processor looks up this username in the user table. A
    # background event has no user; don't invent a nonexistent 'system' user.
    username = user.username if user else None
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
        'user': user,
        'username': username,
        'request_id': request_id,
    }
    # NetBox copies a request whenever this key is present when dispatching
    # webhooks and scripts. Background jobs have no request to copy.
    if request is not None or _LEGACY_EVENT_PIPELINE:
        event_data['request'] = request

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
