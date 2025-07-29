from django.db.models import Q

from aleksis.apps.matrix.models import MatrixProfile, MatrixRoom
from aleksis.core.models import Group

from .tasks import sync_room


def post_save_matrix_signal(sender, instance, created, **kwargs):
    """Sync Matrix room after changing a group/Matrix room/Matrix profile."""
    rooms = []
    if isinstance(instance, Group):
        rooms = MatrixRoom.objects.filter(group=instance)
    elif isinstance(instance, MatrixRoom) and instance.change_tracker.has_changed("group_id"):
        rooms = [instance]
    elif isinstance(instance, MatrixProfile) and instance.change_tracker.changed():
        rooms = MatrixRoom.objects.filter(
            Q(group__members=instance.person) | Q(group__owners=instance.person)
        ).distinct()

    for room in rooms:
        sync_room.delay(room.pk)


def m2m_changed_matrix_signal(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Sync Matrix room after changing group member- and ownerships."""
    if action not in ("post_add", "post_remove", "post_clear"):
        return

    if isinstance(instance, Group):
        groups = [instance]
    else:
        groups = Group.objects.filter(Q(members=instance) | Q(owners=instance)).distinct()

    for room in MatrixRoom.objects.filter(group__in=groups):
        sync_room.delay(room.pk)
