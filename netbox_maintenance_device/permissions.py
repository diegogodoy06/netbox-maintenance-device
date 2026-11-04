from django.db import router, transaction

from core.signals import clear_events
from utilities.exceptions import PermissionsViolation


def save_restricted(instance, user, action):
    """Save `instance`, rolling back unless the result satisfies the user's constraints.

    `user.has_perm()` without an object only proves the user holds the permission on
    *some* objects. Like NetBox's generic edit view, this evaluates the constraints
    against the saved object and raises PermissionsViolation if they don't match. Any
    events queued by the save are discarded with the rolled-back write.
    """
    model = type(instance)
    allowed = model.objects.restrict(user, action)
    try:
        with transaction.atomic(using=router.db_for_write(model)):
            instance.save()
            if not allowed.filter(pk=instance.pk).exists():
                raise PermissionsViolation()
    except PermissionsViolation:
        clear_events.send(sender=model)
        raise
