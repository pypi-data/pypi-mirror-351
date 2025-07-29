from django.utils.translation import gettext as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import BooleanPreference, IntegerPreference, StringPreference

from aleksis.core.registries import site_preferences_registry

matrix = Section("matrix", verbose_name=_("Matrix"))


@site_preferences_registry.register
class Homeserver(StringPreference):
    section = matrix
    name = "homeserver"
    verbose_name = _("URL of Matrix homeserver")
    default = ""
    help_text = _(
        "URL of the Matrix homeserver on which groups and "
        "spaces should be created (e. g. https://matrix.org)"
    )


@site_preferences_registry.register
class HomeserverForIDs(StringPreference):
    section = matrix
    name = "homeserver_ids"
    verbose_name = _("Name of Matrix homeserver used for auto-generating Matrix IDs")
    help_text = _("Leave empty to not create Matrix IDs automatically")
    default = ""


@site_preferences_registry.register
class AccessToken(StringPreference):
    section = matrix
    name = "access_token"
    verbose_name = _("Access token to access homeserver")
    default = ""
    help_text = _(
        "This has to be the access token of a suitable bot user. It is used for all actions."
    )


@site_preferences_registry.register
class DisambiguateRoomAliases(BooleanPreference):
    section = matrix
    name = "disambiguate_room_aliases"
    verbose_name = _("Disambiguate room aliases")
    default = True
    help_text = _("Suffix room aliases with ascending numbers to avoid name clashes")


@site_preferences_registry.register
class UseSpaces(BooleanPreference):
    section = matrix
    name = "use_spaces"
    verbose_name = _("Use Matrix spaces")
    default = True
    help_text = _("This activates the creation and management of Matrix spaces.")


@site_preferences_registry.register
class ReducePowerLevels(BooleanPreference):
    section = matrix
    name = "reduce_power_levels"
    verbose_name = _("Reduce existing power levels")
    default = False
    help_text = _("Reduce power levels of existing members to the level suggested by AlekSIS.")


@site_preferences_registry.register
class PowerLevelForOwners(IntegerPreference):
    section = matrix
    name = "power_level_for_owners"
    verbose_name = _("Power level for owners")
    default = 50
    required = True
    help_text = _("This power level will be set for all owners of a group.")


@site_preferences_registry.register
class PowerLevelForMembers(IntegerPreference):
    section = matrix
    name = "power_level_for_members"
    verbose_name = _("Power level for members")
    default = 0
    required = True
    help_text = _("This power level will be set for all members of a group.")
