from typing import Optional, Union

from django.utils.translation import gettext_lazy as _

from celery.result import AsyncResult

from aleksis.apps.matrix.models import MatrixRoom
from aleksis.apps.matrix.tasks import provision_group_in_matrix
from aleksis.core.models import Group


@Group.method
def provision_in_matrix(self, sync: bool = False) -> Union[MatrixRoom, AsyncResult]:
    """Create and sync a room for this group in Matrix."""
    if sync:
        return self._provision_in_matrix()
    else:
        return provision_group_in_matrix.delay(self.pk)


@Group.method
def _provision_in_matrix(self) -> MatrixRoom:
    """Create and sync a room for this group in Matrix."""
    room = MatrixRoom.from_group(self)
    room.sync()
    return room


@Group.property_
def matrix_alias(self) -> Optional[str]:
    """Return the alias of the group's room in Matrix."""
    rooms = [room for room in self.matrix_rooms.all() if isinstance(room, MatrixRoom)]
    return rooms[0].alias if rooms else None


@Group.property_
def matrix_room_id(self) -> Optional[str]:
    """Return the ID of the group's room in Matrix."""
    rooms = [room for room in self.matrix_rooms.all() if isinstance(room, MatrixRoom)]
    return rooms[0].room_id if rooms else None


Group.add_permission("view_matrixroom", _("Can view matrix room of a group"))
