from django.utils.translation import gettext as _

from aleksis.apps.matrix.tasks import provision_groups_in_matrix
from aleksis.core.forms import ActionForm


def provision_in_matrix_action(modeladmin, request, queryset):
    """Provision selected groups in Matrix."""
    provision_groups_in_matrix.delay(list(queryset.values_list("pk", flat=True)))


provision_in_matrix_action.short_description = _("Provision in Matrix")


class GroupMatrixRoomActionForm(ActionForm):
    def get_actions(self):
        return [provision_in_matrix_action]
