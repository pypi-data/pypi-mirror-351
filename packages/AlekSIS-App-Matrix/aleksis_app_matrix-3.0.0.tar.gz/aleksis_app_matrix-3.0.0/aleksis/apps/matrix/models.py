import re
from typing import Any, Optional, Union

from django.db import models
from django.db.models import Q, QuerySet
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from model_utils import FieldTracker

from aleksis.core.mixins import ExtensibleModel, ExtensiblePolymorphicModel
from aleksis.core.models import Group, Person
from aleksis.core.util.core_helpers import get_site_preferences

from .util.matrix import MatrixException, do_matrix_request


class MatrixProfile(ExtensibleModel):
    """Model for a Matrix profile."""

    matrix_id = models.CharField(max_length=255, verbose_name=_("Matrix ID"), unique=True)
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("Person"),
        null=True,
        blank=True,
        related_name="matrix_profile",
    )

    change_tracker = FieldTracker()

    class Meta:
        verbose_name = _("Matrix profile")
        verbose_name_plural = _("Matrix profiles")

    def __str__(self):
        return self.matrix_id

    @classmethod
    def build_matrix_id(cls, username: str, homeserver: Optional[str] = None) -> str:
        """Build a Matrix ID from a username."""
        homeserver = homeserver or get_site_preferences()["matrix__homeserver_ids"]
        return f"@{username}:{homeserver}"

    @classmethod
    def from_person(cls, person: Person, commit: bool = False) -> Union["MatrixProfile", None]:
        """Get or create a Matrix profile from a person."""
        if hasattr(person, "matrix_profile"):
            return person.matrix_profile
        if not person.user:
            raise ValueError("Person must have a user.")
        if not get_site_preferences()["matrix__homeserver_ids"]:
            return None
        new_profile = MatrixProfile(
            matrix_id=cls.build_matrix_id(person.user.username), person=person
        )
        if commit:
            new_profile.save()
        return new_profile


class MatrixRoom(ExtensiblePolymorphicModel):
    """Model for a Matrix room."""

    room_id = models.CharField(max_length=255, verbose_name=_("Room ID"), unique=True)
    alias = models.CharField(max_length=255, verbose_name=_("Alias"), unique=True, blank=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name=_("Group"),
        related_name="matrix_rooms",
    )

    change_tracker = FieldTracker(["group_id"])

    class Meta:
        verbose_name = _("Matrix room")
        verbose_name_plural = _("Matrix rooms")
        permissions = (("provision_group_in_matrix", "Can provision group in Matrix"),)

    def __str__(self):
        return self.room_id

    @classmethod
    def get_queryset(cls):
        """Get a queryset for only Matrix rooms."""
        return cls.objects.not_instance_of(MatrixSpace)

    @classmethod
    def build_alias(cls, group: Group) -> str:
        """Build a room alias from a group."""
        return slugify(group.short_name or group.name)

    @classmethod
    def from_group(cls, group: Group) -> "MatrixRoom":
        """Get or create a Matrix room from a group."""
        try:
            room = cls.get_queryset().get(group=group)
        except cls.DoesNotExist:
            room = cls(group=group)

        if room.room_id:
            # Existing room, check if still accessible
            r = do_matrix_request("GET", f"directory/list/room/{room.room_id}")
        else:
            # Room does not exist, create it
            alias = cls.build_alias(group)
            profiles_to_invite = list(
                cls.get_profiles_for_group(group).values_list("matrix_id", flat=True)
            )

            alias_found = False
            while not alias_found:
                try:
                    r = cls._create_room(group.name, alias, profiles_to_invite)
                    alias_found = True
                except MatrixException as e:
                    if (
                        not get_site_preferences()["matrix__disambiguate_room_aliases"]
                        or e.args[0].get("errcode") != "M_ROOM_IN_USE"
                    ):
                        raise

                match = re.match(r"^(.*)-(\d+)$", alias)
                if match:
                    # Counter found, increase
                    prefix = match.group(1)
                    counter = int(match.group(2)) + 1
                    alias = f"{prefix}-{counter}"
                else:
                    # Counter not found, add one
                    alias = f"{alias}-2"

            room.room_id = r["room_id"]
            room.alias = r["room_alias"]
            room.save()
        return room

    @classmethod
    def _create_room(
        self,
        name: str,
        alias: str,
        invite: Optional[list[str]] = None,
        creation_content: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a Matrix room."""
        body = {"preset": "private_chat", "name": name, "room_alias_name": alias}

        if invite:
            body["invite"] = invite

        if creation_content:
            body["creation_content"] = creation_content

        try:
            r = do_matrix_request("POST", "createRoom", body=body)
        except MatrixException as e:
            if e.args[0].get("error") == "Cannot invite so many users at once":
                del body["invite"]
                r = do_matrix_request("POST", "createRoom", body=body)
            else:
                raise

        return r

    def get_power_levels(self) -> dict[str, int]:
        """Return the power levels for this room."""
        r = do_matrix_request("GET", f"rooms/{self.room_id}/state")

        event = list(filter(lambda x: x["type"] == "m.room.power_levels", r))
        user_levels = event[0]["content"]["users"]

        return user_levels

    def get_members(self) -> list[str]:
        """Get all members of this room."""
        r = do_matrix_request("GET", f"rooms/{self.room_id}/members")
        return [
            m["state_key"]
            for m in filter(lambda c: c["content"]["membership"] in ("join", "invite"), r["chunk"])
        ]

    def _invite(self, profile: MatrixProfile) -> dict[str, Any]:
        """Invite a user to this room."""
        r = do_matrix_request(
            "POST",
            f"rooms/{self.room_id}/invite",
            body={"user_id": profile.matrix_id},
        )
        return r

    def _set_power_levels(self, power_levels: dict[str, int]) -> dict[str, Any]:
        """Set the power levels for this room."""
        r = do_matrix_request(
            "PUT",
            f"rooms/{self.room_id}/state/m.room.power_levels/",
            body={"users": power_levels},
        )
        return r

    def _ensure_joined(self) -> True:
        r = do_matrix_request("POST", f"join/{self.room_id}")
        return r

    @classmethod
    def get_profiles_for_group(cls, group: Group) -> QuerySet:
        """Get all profile objects for the members/owners of a group."""
        existing_profiles = MatrixProfile.objects.filter(
            Q(person__member_of=group) | Q(person__owner_of=group)
        )
        profiles_to_create = []
        for person in (
            Person.objects.filter(user__isnull=False)
            .filter(Q(member_of=group) | Q(owner_of=group))
            .exclude(matrix_profile__in=existing_profiles)
            .distinct()
        ):
            new_profile = MatrixProfile.from_person(person)
            if new_profile:
                profiles_to_create.append(new_profile)
        MatrixProfile.objects.bulk_create(profiles_to_create)

        all_profiles = MatrixProfile.objects.filter(
            Q(person__in=group.members.all()) | Q(person__in=group.owners.all())
        ).distinct()

        return all_profiles

    def get_profiles(self) -> QuerySet:
        """Get all profile objects for the members/owners of this group."""
        return self.get_profiles_for_group(self.group)

    def sync_profiles(self):
        """Sync profiles for this room."""
        all_profiles = self.get_profiles()
        members = self.get_members()

        # Invite all users who are not in the room yet
        for profile in all_profiles:
            if profile.matrix_id not in members:
                # Now invite
                self._invite(profile)

        # Set power levels for all users
        user_levels = self.get_power_levels()
        for profile in all_profiles:
            if profile.person in self.group.owners.all():
                power_level = get_site_preferences()["matrix__power_level_for_owners"]
            else:
                power_level = get_site_preferences()["matrix__power_level_for_members"]

            if (
                profile.matrix_id not in user_levels
                or user_levels[profile.matrix_id] < power_level
                or get_site_preferences()["matrix__reduce_power_levels"]
            ):
                user_levels[profile.matrix_id] = power_level
        self._set_power_levels(user_levels)

    def sync_space(self):
        """Sync the space for this room."""
        if self.group.child_groups.all():
            # Do space stuff
            space = MatrixSpace.from_group(self.group)
            space.sync()
        return None

    def sync_room_params(self):
        """Sync all room-specific parameters, e. g. the name."""
        self._ensure_joined()

    def sync(self):
        """Sync this room."""
        self.sync_room_params()
        self.sync_profiles()
        if get_site_preferences()["matrix__use_spaces"]:
            self.sync_space()


class MatrixSpace(MatrixRoom):
    children = models.ManyToManyField(
        to=MatrixRoom, verbose_name=_("Child rooms/spaces"), blank=True, related_name="parents"
    )

    class Meta:
        verbose_name = _("Matrix space")
        verbose_name_plural = _("Matrix spaces")

    def __str__(self):
        return self.room_id

    @classmethod
    def get_queryset(cls):
        """Get a queryset with only Matrix spaces."""
        return cls.objects.instance_of(MatrixSpace)

    @classmethod
    def build_alias(cls, group: Group) -> str:
        """Build an alias for this space."""
        return slugify(group.short_name or group.name) + "-space"

    @classmethod
    def _create_room(
        self,
        name: str,
        alias: str,
        invite: Optional[list[str]] = None,
        creation_content: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a Matrix space."""
        if not creation_content:
            creation_content = {}
        creation_content["type"] = "m.space"
        return super()._create_room(name, alias, invite, creation_content)

    def get_children(self) -> list[str]:
        """Get all children (rooms/spaces) of this space."""
        r = do_matrix_request("GET", f"rooms/{self.room_id}/state")
        return [c["state_key"] for c in r if c["type"] == "m.space.child"]

    def _add_child(self, room_id: str) -> dict[str, Any]:
        """Add a child room to this space."""
        r = do_matrix_request(
            "PUT",
            f"/_matrix/client/v3/rooms/{self.room_id}/state/m.space.child/{room_id}",
            body={"via": [get_site_preferences()["matrix__homeserver_ids"]]},
        )
        return r

    def sync_children(self):
        """Sync membership of child spaces and rooms."""
        current_children = self.get_children()
        child_spaces = (
            MatrixSpace.get_queryset()
            .filter(group__in=self.group.child_groups.filter(child_groups__isnull=False))
            .values_list("room_id", flat=True)
        )
        child_rooms = (
            MatrixRoom.get_queryset()
            .filter(
                Q(group__in=self.group.child_groups.filter(child_groups__isnull=True))
                | Q(group=self.group)
            )
            .values_list("room_id", flat=True)
        )

        child_ids = list(child_spaces) + list(child_rooms)

        missing_ids = set(child_ids).difference(set(current_children))

        for missing_id in missing_ids:
            self._add_child(missing_id)

    def ensure_children(self):
        """Ensure that all child rooms/spaces exist."""
        for group in self.group.child_groups.all().prefetch_related("child_groups"):
            group.provision_in_matrix(sync=True)
            if group.child_groups.all():
                space = MatrixSpace.from_group(group)
                space.ensure_children()
                space.sync_children()

    def sync(self):
        """Sync this space."""
        self.sync_room_params()
        self.ensure_children()
        self.sync_children()
        self.sync_profiles()
