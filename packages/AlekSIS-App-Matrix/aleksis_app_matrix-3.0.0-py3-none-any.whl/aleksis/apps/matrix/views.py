from django.utils.decorators import method_decorator

from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from guardian.shortcuts import get_objects_for_user
from rules.contrib.views import PermissionRequiredMixin

from aleksis.apps.matrix.filters import GroupMatrixRoomFilter
from aleksis.apps.matrix.forms import GroupMatrixRoomActionForm
from aleksis.apps.matrix.tables import GroupsMatrixRoomsTable
from aleksis.core.decorators import pwa_cache
from aleksis.core.models import Group


@method_decorator(pwa_cache, name="dispatch")
class MatrixRoomListView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    """Overview about groups and their Matrix rooms."""

    model = Group
    template_name = "matrix/room/list.html"
    permission_required = "matrix.view_matrixrooms_rule"
    table_class = GroupsMatrixRoomsTable
    filterset_class = GroupMatrixRoomFilter

    def get_queryset(self):
        return get_objects_for_user(
            self.request.user, ["core.view_group", "core.view_matrixroom"], Group
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.action_form = GroupMatrixRoomActionForm(
            self.request, self.request.POST or None, queryset=self.get_queryset()
        )
        context["action_form"] = self.action_form
        return context

    def post(self, request, *args, **kwargs):
        r = super().get(request, *args, **kwargs)
        if self.action_form.is_valid() and request.user.has_perm(
            "matrix.provision_group_in_matrix_rule"
        ):
            self.action_form.execute()
        return r
