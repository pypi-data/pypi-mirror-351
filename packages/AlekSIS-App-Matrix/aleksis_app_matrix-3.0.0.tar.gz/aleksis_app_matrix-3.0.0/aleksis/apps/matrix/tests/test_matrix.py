from datetime import date
from unittest.mock import call

from django.contrib.auth.models import User

import pytest
import requests

from aleksis.apps.matrix.models import MatrixProfile, MatrixRoom, MatrixSpace
from aleksis.apps.matrix.util.matrix import (
    MatrixException,
    build_url,
    do_matrix_request,
)
from aleksis.core.models import Group, Person, SchoolTerm
from aleksis.core.util.core_helpers import get_site_preferences

pytestmark = pytest.mark.django_db

SERVER_URL = "http://127.0.0.1:8008"


def test_connection(synapse):
    assert synapse["listeners"][0]["port"] == 8008

    assert requests.get(SERVER_URL).status_code == requests.codes.ok  # noqa: S113


@pytest.fixture
def matrix_bot_user(synapse):
    body = {"username": "aleksis-bot", "password": "test", "auth": {"type": "m.login.dummy"}}

    get_site_preferences()["matrix__homeserver"] = SERVER_URL

    r = requests.post(build_url("register"), json=body)  # noqa: S113
    print(r.text, build_url("register"))
    assert r.status_code == requests.codes.ok

    user = r.json()

    get_site_preferences()["matrix__access_token"] = user["access_token"]

    yield user


def test_matrix_bot_user(matrix_bot_user):
    print(matrix_bot_user)
    assert True


def test_create_room_for_group(matrix_bot_user):
    g = Group.objects.create(name="Test Room")
    assert not MatrixRoom.objects.all().exists()
    room = MatrixRoom.from_group(g)

    assert ":matrix.aleksis.example.org" in room.room_id
    assert room.alias == "#test-room:matrix.aleksis.example.org"

    # On second get, it should be the same matrix room
    assert MatrixRoom.from_group(g) == room

    r = do_matrix_request("GET", f"rooms/{room.room_id}/aliases")
    aliases = r["aliases"]
    assert "#test-room:matrix.aleksis.example.org" in aliases


#
def test_create_room_for_group_short_name(matrix_bot_user):
    g = Group.objects.create(name="Test Room", short_name="test")
    assert not MatrixRoom.objects.all().exists()
    room = MatrixRoom.from_group(g)
    assert room.alias == "#test:matrix.aleksis.example.org"


def test_room_alias_collision_same_name(matrix_bot_user):
    g1 = Group.objects.create(name="Test Room")
    g2 = Group.objects.create(name="test-room")
    g3 = Group.objects.create(name="Test-Room")
    g4 = Group.objects.create(name="test room")

    get_site_preferences()["matrix__disambiguate_room_aliases"] = True

    room = MatrixRoom.from_group(g1)
    assert room.alias == "#test-room:matrix.aleksis.example.org"

    room = MatrixRoom.from_group(g2)
    assert room.alias == "#test-room-2:matrix.aleksis.example.org"

    room = MatrixRoom.from_group(g3)
    assert room.alias == "#test-room-3:matrix.aleksis.example.org"

    get_site_preferences()["matrix__disambiguate_room_aliases"] = False

    with pytest.raises(MatrixException):
        MatrixRoom.from_group(g4)


def test_room_alias_collision_school_term(matrix_bot_user):
    get_site_preferences()["matrix__disambiguate_room_aliases"] = True

    school_term_a = SchoolTerm.objects.create(
        name="Test Term A", date_start=date(2020, 1, 1), date_end=date(2020, 12, 31)
    )
    school_term_b = SchoolTerm.objects.create(
        name="Test Term B", date_start=date(2021, 1, 1), date_end=date(2021, 12, 31)
    )
    g1 = Group.objects.create(name="Test Room", school_term=school_term_a)
    g2 = Group.objects.create(name="Test Room", school_term=school_term_b)

    room = MatrixRoom.from_group(g1)
    assert room.alias == "#test-room:matrix.aleksis.example.org"

    room = MatrixRoom.from_group(g2)
    assert room.alias == "#test-room-2:matrix.aleksis.example.org"


def test_sync_room_members(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"
    get_site_preferences()["matrix__reduce_power_levels"] = False
    get_site_preferences()["matrix__power_level_for_owners"] = 50
    get_site_preferences()["matrix__power_level_for_members"] = 0

    g = Group.objects.create(name="Test Room")
    u1 = User.objects.create_user("test1", "test1@example.org", "test1")
    u2 = User.objects.create_user("test2", "test2@example.org", "test2")
    u3 = User.objects.create_user("test3", "test3@example.org", "test3")
    u4 = User.objects.create_user("test4", "test4@example.org", "test4")
    u5 = User.objects.create_user("test5", "test5@example.org", "test5")

    p1 = Person.objects.create(first_name="Test", last_name="Person", user=u1)
    p2 = Person.objects.create(first_name="Test 2", last_name="Person", user=u2)
    p3 = Person.objects.create(first_name="Test 3", last_name="Person", user=u3)
    p4 = Person.objects.create(first_name="Test 4", last_name="Person", user=u4)
    p5 = Person.objects.create(first_name="Test 5", last_name="Person", user=u5)

    g.members.set([p1, p2, p3])
    g.owners.set([p4, p5])

    room = MatrixRoom.from_group(g)
    room.sync_profiles()

    assert MatrixProfile.objects.all().count() == 5
    assert p1.matrix_profile
    assert p1.matrix_profile.matrix_id == "@test1:matrix.aleksis.example.org"
    assert p2.matrix_profile
    assert p2.matrix_profile.matrix_id == "@test2:matrix.aleksis.example.org"
    assert p3.matrix_profile
    assert p3.matrix_profile.matrix_id == "@test3:matrix.aleksis.example.org"
    assert p4.matrix_profile
    assert p4.matrix_profile.matrix_id == "@test4:matrix.aleksis.example.org"
    assert p5.matrix_profile
    assert p5.matrix_profile.matrix_id == "@test5:matrix.aleksis.example.org"

    # Check members
    r = do_matrix_request(
        "GET",
        f"rooms/{room.room_id}/members",
        body={"membership": ["join", "invite"]},
    )

    matrix_ids = [x["state_key"] for x in r["chunk"]]
    assert p1.matrix_profile.matrix_id in matrix_ids
    assert p2.matrix_profile.matrix_id in matrix_ids
    assert p3.matrix_profile.matrix_id in matrix_ids
    assert p4.matrix_profile.matrix_id in matrix_ids
    assert p5.matrix_profile.matrix_id in matrix_ids

    # Get power levels
    r = do_matrix_request("GET", f"rooms/{room.room_id}/state")
    for event in r:
        if event["type"] != "m.room.power_levels":
            continue
        current_power_levels = event["content"]["users"]

        assert current_power_levels[p1.matrix_profile.matrix_id] == 0
        assert current_power_levels[p2.matrix_profile.matrix_id] == 0
        assert current_power_levels[p3.matrix_profile.matrix_id] == 0
        assert current_power_levels[p4.matrix_profile.matrix_id] == 50
        assert current_power_levels[p5.matrix_profile.matrix_id] == 50

        break


def test_power_levels(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"
    get_site_preferences()["matrix__power_level_for_owners"] = 55
    get_site_preferences()["matrix__power_level_for_members"] = 11
    get_site_preferences()["matrix__reduce_power_levels"] = False

    g = Group.objects.create(name="Test Room")
    u1 = User.objects.create_user("test1", "test1@example.org", "test1")
    u2 = User.objects.create_user("test2", "test2@example.org", "test2")

    p1 = Person.objects.create(first_name="Test", last_name="Person", user=u1)
    p2 = Person.objects.create(first_name="Test 2", last_name="Person", user=u2)

    g.members.set([p1])
    g.owners.set([p2])

    room = MatrixRoom.from_group(g)
    room.sync_profiles()

    # Get power levels
    r = do_matrix_request("GET", f"rooms/{room.room_id}/state")
    for event in r:
        if event["type"] != "m.room.power_levels":
            continue
        current_power_levels = event["content"]["users"]

        assert current_power_levels[p1.matrix_profile.matrix_id] == 11
        assert current_power_levels[p2.matrix_profile.matrix_id] == 55

        break

    # Test reducing of power levels
    g.owners.set([])
    g.members.set([p1, p2])

    room.sync_profiles()

    # Not reduced here
    r = do_matrix_request("GET", f"rooms/{room.room_id}/state")
    for event in r:
        if event["type"] != "m.room.power_levels":
            continue
        current_power_levels = event["content"]["users"]

        assert current_power_levels[p1.matrix_profile.matrix_id] == 11
        assert current_power_levels[p2.matrix_profile.matrix_id] == 55

        break

    get_site_preferences()["matrix__reduce_power_levels"] = True
    room.sync_profiles()

    # Reduced here
    r = do_matrix_request("GET", f"rooms/{room.room_id}/state")
    for event in r:
        if event["type"] != "m.room.power_levels":
            continue
        current_power_levels = event["content"]["users"]

        assert current_power_levels[p1.matrix_profile.matrix_id] == 11
        assert current_power_levels[p2.matrix_profile.matrix_id] == 11

        break


def test_sync_room_members_without_user(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    g = Group.objects.create(name="Test Room")
    u1 = User.objects.create_user("test1", "test1@example.org", "test1")

    p1 = Person.objects.create(first_name="Test", last_name="Person", user=u1)
    p2 = Person.objects.create(first_name="Test 2", last_name="Person")

    g.members.set([p1, p2])

    room = MatrixRoom.from_group(g)
    room.sync_profiles()

    assert MatrixProfile.objects.all().count() == 1
    assert p1.matrix_profile
    assert p1.matrix_profile.matrix_id == "@test1:matrix.aleksis.example.org"
    assert not hasattr(p2, "matrix_profile")


# test no homeserver for ids


def test_sync_room_members_without_homeserver(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = ""

    g = Group.objects.create(name="Test Room")
    u1 = User.objects.create_user("test1", "test1@example.org", "test1")

    p1 = Person.objects.create(first_name="Test", last_name="Person", user=u1)
    p2 = Person.objects.create(first_name="Test 2", last_name="Person")

    MatrixProfile.objects.create(person=p2, matrix_id="@test2:matrix.aleksis.example.org")
    g.members.set([p1, p2])

    room = MatrixRoom.from_group(g)
    room.sync_profiles()

    assert MatrixProfile.objects.all().count() == 1
    assert not hasattr(p1, "matrix_profile")
    assert p2.matrix_profile
    assert p2.matrix_profile.matrix_id == "@test2:matrix.aleksis.example.org"


def test_use_room_sync(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    g = Group.objects.create(name="Test Room")
    u1 = User.objects.create_user("test1", "test1@example.org", "test1")

    p1 = Person.objects.create(first_name="Test", last_name="Person", user=u1)

    g.members.add(p1)

    r = g.provision_in_matrix(sync=True)

    assert isinstance(r, MatrixRoom)

    assert MatrixProfile.objects.all().count() == 1
    assert p1.matrix_profile
    assert p1.matrix_profile.matrix_id == "@test1:matrix.aleksis.example.org"


def test_space_creation(matrix_bot_user):
    parent_group = Group.objects.create(name="Test Group")
    child_1 = Group.objects.create(name="Test Group 1")
    child_2 = Group.objects.create(name="Test Group 2")
    child_3 = Group.objects.create(name="Test Group 3")
    parent_group.child_groups.set([child_1, child_2, child_3])

    parent_group.provision_in_matrix(sync=True)

    get_site_preferences()["matrix__use_spaces"] = True

    space = MatrixSpace.from_group(parent_group)

    r = do_matrix_request("GET", f"rooms/{space.room_id}/state")

    events = {x["type"]: x for x in r}

    assert events["m.room.create"]["content"]["type"] == "m.space"

    space.ensure_children()

    rooms = MatrixRoom.get_queryset().values_list("group_id", flat=True)
    assert child_1.pk in rooms
    assert child_2.pk in rooms
    assert child_3.pk in rooms

    space.sync_children()

    r = do_matrix_request("GET", f"rooms/{space.room_id}/state")
    interesting_events = [x["state_key"] for x in r if x["type"] == "m.space.child"]

    assert len(interesting_events) == 4

    rooms = list(
        MatrixRoom.get_queryset()
        .filter(group__in=[parent_group, child_1, child_2, child_3])
        .values_list("room_id", flat=True)
    )

    assert len(rooms) == 4

    assert set(interesting_events) == set(rooms)


def test_space_creation_with_child_spaces(matrix_bot_user):
    parent_group = Group.objects.create(name="Test Group")
    child_1 = Group.objects.create(name="Test Group 1")
    child_1_child_1 = Group.objects.create(name="Test Group 1 1")
    child_1_child_2 = Group.objects.create(name="Test Group 1 2")
    child_1.child_groups.set([child_1_child_1, child_1_child_2])
    child_2 = Group.objects.create(name="Test Group 2")
    child_3 = Group.objects.create(name="Test Group 3")
    parent_group.child_groups.set([child_1, child_2, child_3])

    parent_group.provision_in_matrix(sync=True)

    get_site_preferences()["matrix__use_spaces"] = True

    space = MatrixSpace.from_group(parent_group)

    space.ensure_children()

    rooms = MatrixRoom.get_queryset().values_list("group_id", flat=True)
    assert child_1.pk in rooms
    assert child_2.pk in rooms
    assert child_3.pk in rooms
    assert child_1_child_1.pk in rooms
    assert child_1_child_2.pk in rooms

    spaces = MatrixSpace.get_queryset().values_list("group_id", flat=True)
    assert parent_group.pk in spaces
    assert child_1.pk in spaces

    space.sync_children()

    r = do_matrix_request("GET", f"rooms/{space.room_id}/state")
    interesting_events = [x["state_key"] for x in r if x["type"] == "m.space.child"]

    assert len(interesting_events) == 4

    rooms = list(
        MatrixRoom.get_queryset()
        .filter(group__in=[parent_group, child_2, child_3])
        .values_list("room_id", flat=True)
    ) + list(MatrixSpace.objects.filter(group=child_1).values_list("room_id", flat=True))

    assert len(rooms) == 4

    assert set(interesting_events) == set(rooms)

    space = MatrixSpace.objects.get(group=child_1)

    r = do_matrix_request("GET", f"rooms/{space.room_id}/state")
    interesting_events = [x["state_key"] for x in r if x["type"] == "m.space.child"]

    assert len(interesting_events) == 3

    rooms = list(
        MatrixRoom.get_queryset()
        .filter(group__in=[child_1, child_1_child_1, child_1_child_2])
        .values_list("room_id", flat=True)
    )

    assert len(rooms) == 3

    assert set(interesting_events) == set(rooms)


def test_alias_room_id_using_group(matrix_bot_user):
    g = Group.objects.create(name="Test Room")
    room = MatrixRoom.from_group(g)
    child_1 = Group.objects.create(name="Test Group 1")
    g.child_groups.set([child_1])
    room.sync()

    assert MatrixSpace.objects.get_queryset().count() == 1

    assert g.matrix_room_id == room.room_id
    assert g.matrix_alias == room.alias


def test_matrix_profile():
    p1 = Person.objects.create(first_name="Test", last_name="Person")

    with pytest.raises(ValueError):
        profile = MatrixProfile.from_person(p1)

    p1.user = User.objects.create(username="test")
    p1.save()

    profile = MatrixProfile.from_person(p1)

    assert profile == MatrixProfile.from_person(p1)


def test_too_much_invites(matrix_bot_user):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    g = Group.objects.create(name="Test Room")

    persons = []
    for i in range(100):
        u = User.objects.create_user(f"test{i}", f"test{i}@example.org", f"test{i}")
        p = Person.objects.create(first_name=f"Test {i}", last_name="Person", user=u)
        persons.append(p)

    g.members.set(persons)

    room = MatrixRoom.from_group(g)

    room.sync_profiles()


def test_signal_group_changed(matrix_bot_user, mocker):
    g = Group.objects.create(name="Test Room")
    room = MatrixRoom.from_group(g)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    g.name = "Test Room 2"
    g.save()

    sync_mock.assert_called_once_with(room.pk)


def test_signal_room_group_changed(matrix_bot_user, mocker):
    g = Group.objects.create(name="Test Room")
    g2 = Group.objects.create(name="Test Room 2")
    room = MatrixRoom.from_group(g)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    room.group = g2
    room.save()

    sync_mock.assert_called_once_with(room.pk)


def test_signal_profile_person_changed(matrix_bot_user, mocker):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    p = Person.objects.create(
        first_name="Test", last_name="Person", user=User.objects.create(username="test")
    )
    p2 = Person.objects.create(
        first_name="Test 2", last_name="Person 2", user=User.objects.create(username="test2")
    )
    p3 = Person.objects.create(
        first_name="Test 3", last_name="Person 3", user=User.objects.create(username="test3")
    )
    p4 = Person.objects.create(
        first_name="Test 4", last_name="Person 4", user=User.objects.create(username="test4")
    )

    g = Group.objects.create(name="Test Room")
    g.members.set([p])
    g.owners.set([p3])

    g2 = Group.objects.create(name="Test Room 2")
    g2.members.set([p2])
    g2.owners.set([p4])

    MatrixRoom.from_group(g)
    room2 = MatrixRoom.from_group(g2)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    profile = MatrixProfile.from_person(p)
    p2.matrix_profile.delete()
    profile.person = p2
    profile.save()

    sync_mock.assert_called_with(room2.pk)

    profile2 = MatrixProfile.from_person(p3)
    p4.matrix_profile.delete()
    profile2.person = p4
    profile2.save()

    sync_mock.assert_called_with(room2.pk)


def test_signal_room_members_changed(matrix_bot_user, mocker):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    p = Person.objects.create(
        first_name="Test", last_name="Person", user=User.objects.create(username="test")
    )
    p2 = Person.objects.create(
        first_name="Test 2", last_name="Person 2", user=User.objects.create(username="test2")
    )
    p3 = Person.objects.create(
        first_name="Test 3", last_name="Person 3", user=User.objects.create(username="test3")
    )
    p4 = Person.objects.create(
        first_name="Test 4", last_name="Person 4", user=User.objects.create(username="test4")
    )

    g = Group.objects.create(name="Test Room")
    g.members.set([p])

    room = MatrixRoom.from_group(g)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    g.members.set([p2, p3])

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.members.add(p4)

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.members.remove(p2)

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.members.clear()

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()


def test_signal_room_owners_changed(matrix_bot_user, mocker):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    p = Person.objects.create(
        first_name="Test", last_name="Person", user=User.objects.create(username="test")
    )
    p2 = Person.objects.create(
        first_name="Test 2", last_name="Person 2", user=User.objects.create(username="test2")
    )
    p3 = Person.objects.create(
        first_name="Test 3", last_name="Person 3", user=User.objects.create(username="test3")
    )
    p4 = Person.objects.create(
        first_name="Test 4", last_name="Person 4", user=User.objects.create(username="test4")
    )

    g = Group.objects.create(name="Test Room")
    g.owners.set([p])

    room = MatrixRoom.from_group(g)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    g.owners.set([p2, p3])

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.owners.add(p4)

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.owners.remove(p2)

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()

    g.owners.clear()

    sync_mock.assert_called_with(room.pk)
    sync_mock.reset_mock()


def test_signal_room_members_changed_reverse(matrix_bot_user, mocker):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    p = Person.objects.create(
        first_name="Test", last_name="Person", user=User.objects.create(username="test")
    )

    g = Group.objects.create(name="Test Room")
    g2 = Group.objects.create(name="Test Room 2")

    room = MatrixRoom.from_group(g)
    room2 = MatrixRoom.from_group(g2)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    p.member_of.set([g, g2])

    sync_mock.assert_has_calls([call(room.pk), call(room2.pk)])
    sync_mock.reset_mock()


def test_signal_room_owners_changed_reverse(matrix_bot_user, mocker):
    get_site_preferences()["matrix__homeserver_ids"] = "matrix.aleksis.example.org"

    p = Person.objects.create(
        first_name="Test", last_name="Person", user=User.objects.create(username="test")
    )

    g = Group.objects.create(name="Test Room")
    g2 = Group.objects.create(name="Test Room 2")

    room = MatrixRoom.from_group(g)
    room2 = MatrixRoom.from_group(g2)

    sync_mock = mocker.patch("aleksis.apps.matrix.tasks.sync_room.delay")

    p.owner_of.set([g, g2])

    sync_mock.assert_has_calls([call(room.pk), call(room2.pk)])
    sync_mock.reset_mock()
