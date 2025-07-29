from collections.abc import Sequence
from datetime import timedelta

from aleksis.apps.matrix.models import MatrixRoom
from aleksis.core.celery import app
from aleksis.core.models import Group


@app.task
def sync_room(pk: int):
    """Synchronise a Matrix room."""
    room = MatrixRoom.objects.get(pk=pk)
    room.sync()


@app.task
def provision_groups_in_matrix(pks: Sequence[int]):
    """Provision provided groups in Matrix."""
    groups = Group.objects.filter(pk__in=pks)
    for group in groups:
        group._provision_in_matrix()


@app.task
def provision_group_in_matrix(pk: int):
    """Provision provided group in Matrix."""
    group = Group.objects.get(pk=pk)
    group._provision_in_matrix()


@app.task(run_every=timedelta(days=1))
def sync_rooms():
    """Synchronise all Matrix rooms."""
    rooms = MatrixRoom.objects.all()
    for room in rooms:
        sync_room.delay(room.pk)
