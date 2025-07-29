from django.utils.translation import gettext as _

from django_filters import FilterSet, ModelChoiceFilter, ModelMultipleChoiceFilter
from material import Layout, Row

from aleksis.core.filters import MultipleCharFilter
from aleksis.core.models import Group, GroupType, SchoolTerm


class GroupMatrixRoomFilter(FilterSet):
    """Custom filter for groups on Matrix room overview."""

    school_term = ModelChoiceFilter(queryset=SchoolTerm.objects.all())
    group_type = ModelChoiceFilter(queryset=GroupType.objects.all())
    parent_groups = ModelMultipleChoiceFilter(queryset=Group.objects.all())

    search = MultipleCharFilter(["name__icontains", "short_name__icontains"], label=_("Search"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.layout = Layout(Row("search"), Row("school_term", "group_type", "parent_groups"))
        self.form.initial = {"school_term": SchoolTerm.current}
