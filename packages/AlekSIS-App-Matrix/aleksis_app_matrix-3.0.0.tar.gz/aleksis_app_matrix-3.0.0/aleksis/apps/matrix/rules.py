# View groups
import rules

from aleksis.core.models import Group
from aleksis.core.rules import view_group_predicate, view_groups_predicate
from aleksis.core.util.predicates import has_any_object, has_global_perm, has_object_perm

view_matrix_rooms_predicate = view_groups_predicate & (
    has_global_perm("matrix.view_matrixroom") | has_any_object("core.view_matrixroom", Group)
)
rules.add_perm("matrix.view_matrixrooms_rule", view_matrix_rooms_predicate)

view_matrix_room_predicate = view_group_predicate & (
    has_global_perm("matrix.view_matrixroom") | has_object_perm("core.view_matrixroom")
)
rules.add_perm("matrix.view_matrixroom_rule", view_matrix_room_predicate)

provision_room_for_matrix_predicate = view_matrix_room_predicate & (
    has_global_perm("matrix.provision_group_in_matrix")
)
rules.add_perm("matrix.provision_group_in_matrix_rule", provision_room_for_matrix_predicate)

show_menu_predicate = view_matrix_rooms_predicate
rules.add_perm("matrix.show_menu_rule", show_menu_predicate)
