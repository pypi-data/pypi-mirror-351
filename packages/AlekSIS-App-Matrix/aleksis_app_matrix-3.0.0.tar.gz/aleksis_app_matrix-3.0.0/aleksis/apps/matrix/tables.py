from django_tables2 import Column, Table

from aleksis.core.util.tables import SelectColumn


class GroupsMatrixRoomsTable(Table):
    """Table to list groups together with their Matrix rooms."""

    class Meta:
        attrs = {"class": "highlight"}

    selected = SelectColumn()
    name = Column()
    short_name = Column()
    matrix_alias = Column()
    matrix_room_id = Column()
