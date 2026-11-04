from django.db import router, transaction

from core.signals import clear_events
from utilities.exceptions import PermissionsViolation


def write_restricted(model, write, user, action):
    """Run `write()`, rolling back unless the object it returns satisfies the user's constraints.

    `user.has_perm()` without an object only proves the user holds the permission on
    *some* objects. Like NetBox's generic edit view, this evaluates the constraints
    against the saved object and raises PermissionsViolation if they don't match. Any
    events queued by the write are discarded along with it.
    """
    allowed = model.objects.restrict(user, action)
    try:
        with transaction.atomic(using=router.db_for_write(model)):
            instance = write()
            if not allowed.filter(pk=instance.pk).exists():
                raise PermissionsViolation()
    except PermissionsViolation:
        clear_events.send(sender=model)
        raise
    return instance


def save_restricted(instance, user, action):
    """Save `instance` under the rules of `write_restricted()`."""
    def write():
        instance.save()
        return instance
    return write_restricted(type(instance), write, user, action)
