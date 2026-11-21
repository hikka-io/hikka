from client_requests import request_notification_group_seen
from client_requests import request_notification_groups
from client_requests import request_notifications_count
from app.models import Notification
from app.utils import to_timestamp
from datetime import datetime
from fastapi import status
from app import constants
import uuid


def make_notification(user, notification_type, created, data, **kwargs):
    return Notification(
        **{
            "notification_type": notification_type,
            "user_id": user.id,
            "created": created,
            "updated": created,
            "log_id": None,
            "seen": False,
            "data": data,
            **kwargs,
        }
    )


def collection_vote(user, created, score, slug="collection", initiator=None):
    return make_notification(
        user,
        constants.NOTIFICATION_COLLECTION_VOTE,
        created,
        # Like the producer: downvotes carry no identity at all
        {
            "slug": slug,
            "user_score": score,
            "username": initiator.username if initiator else None,
        },
        initiator_user_id=initiator.id if initiator else None,
    )


def edit_accepted(user, created, edit_id, initiator):
    return make_notification(
        user,
        constants.NOTIFICATION_EDIT_ACCEPTED,
        created,
        {"edit_id": edit_id, "description": "", "username": initiator.username},
        initiator_user_id=initiator.id,
    )


def hikka_update(user, created):
    return make_notification(
        user, constants.NOTIFICATION_HIKKA_UPDATE, created, {}
    )


def thirdparty_login(user, created, client_reference):
    return make_notification(
        user,
        constants.NOTIFICATION_THIRDPARTY_LOGIN,
        created,
        {"client": {"reference": client_reference, "name": "app"}},
    )


# All in the afternoon UTC, so the same date in Kyiv.
def at(day, hour):
    return datetime(2026, 11, day, hour)


async def test_notification_groups(
    client,
    create_test_user,
    create_dummy_user,
    moderator_user,
    get_test_token,
    test_session,
):
    user = create_test_user
    client_a, client_b = str(uuid.uuid4()), str(uuid.uuid4())

    test_session.add_all(
        [
            # Upvotes interleaved with other types still form one group
            collection_vote(user, at(7, 10), 1, "a", create_dummy_user),
            edit_accepted(user, at(7, 11), 1, moderator_user),
            collection_vote(user, at(7, 12), 1, "b", moderator_user),
            collection_vote(user, at(7, 13), 1, "a", create_dummy_user),
            # A downvote does not join upvotes
            collection_vote(user, at(7, 14), -1),
            edit_accepted(user, at(7, 15), 2, moderator_user),
            # Updates never group
            hikka_update(user, at(7, 16)),
            hikka_update(user, at(7, 17)),
            # Logins group per application
            thirdparty_login(user, at(6, 10), client_a),
            thirdparty_login(user, at(6, 11), client_b),
            thirdparty_login(user, at(6, 12), client_a),
            # Same type on another day is another group
            edit_accepted(user, at(6, 13), 3, moderator_user),
        ]
    )
    await test_session.commit()

    response = await request_notification_groups(client, get_test_token)
    assert response.status_code == status.HTTP_200_OK

    groups = response.json()["list"]
    summary = [(group["notification_type"], group["count"]) for group in groups]

    assert summary == [
        (constants.NOTIFICATION_HIKKA_UPDATE, 1),
        (constants.NOTIFICATION_HIKKA_UPDATE, 1),
        (constants.NOTIFICATION_EDIT_ACCEPTED, 2),
        (constants.NOTIFICATION_COLLECTION_VOTE, 1),
        (constants.NOTIFICATION_COLLECTION_VOTE, 3),
        (constants.NOTIFICATION_EDIT_ACCEPTED, 1),
        (constants.NOTIFICATION_THIRDPARTY_LOGIN, 2),
        (constants.NOTIFICATION_THIRDPARTY_LOGIN, 1),
    ]
    assert response.json()["pagination"]["total"] == 8

    upvotes = groups[4]
    assert upvotes["reference"] == "collection_vote:1:2026-11-07"
    assert upvotes["unseen"] == 3
    assert upvotes["actors"] == 2
    assert upvotes["targets"] == 2
    assert upvotes["created"] == to_timestamp(at(7, 13))

    # Members come newest first
    created = [n["created"] for n in upvotes["notifications"]]
    assert created == sorted(created, reverse=True)

    # Anonymous downvotes have no actors
    assert groups[3]["actors"] == 0

    edits = groups[2]
    assert edits["actors"] == 1
    assert edits["targets"] == 2


async def test_notification_groups_count_legacy_actors(
    client, create_test_user, create_dummy_user, get_test_token, test_session
):
    def follow(hour, username, initiator=None):
        return make_notification(
            create_test_user,
            constants.NOTIFICATION_FOLLOW,
            at(7, hour),
            {"username": username, "avatar": ""},
            initiator_user_id=initiator.id if initiator else None,
        )

    # Rows created before `initiator_user_id` existed only carry a username
    test_session.add_all(
        [
            follow(10, "old_a"),
            follow(11, "old_b"),
            follow(12, "old_a"),
            # The same account before and after the column was added
            follow(13, create_dummy_user.username),
            follow(14, create_dummy_user.username, create_dummy_user),
        ]
    )
    await test_session.commit()

    response = await request_notification_groups(client, get_test_token)
    [group] = response.json()["list"]

    assert group["count"] == 5
    assert group["actors"] == 3


async def test_notification_groups_hide_legacy_downvoters(
    client, create_test_user, create_dummy_user, get_test_token, test_session
):
    # Older downvotes still stored the voter
    test_session.add_all(
        [
            make_notification(
                create_test_user,
                constants.NOTIFICATION_COMMENT_VOTE,
                at(7, hour),
                {
                    "comment_reference": "c",
                    "user_score": -1,
                    "username": create_dummy_user.username,
                },
            )
            for hour in (10, 11)
        ]
    )
    await test_session.commit()

    response = await request_notification_groups(client, get_test_token)
    [group] = response.json()["list"]

    assert group["count"] == 2
    assert group["actors"] == 0
    for notification in group["notifications"]:
        assert notification["initiator_user"] is None
        assert "username" not in notification["data"]
        assert "avatar" not in notification["data"]
        assert notification["data"]["user_score"] == -1


async def test_notification_groups_count_renamed_actor_once(
    client, create_test_user, create_dummy_user, get_test_token, test_session
):
    # One account voted, renamed, and voted again on the same day
    test_session.add_all(
        [
            make_notification(
                create_test_user,
                constants.NOTIFICATION_COLLECTION_VOTE,
                at(7, hour),
                {"slug": "c", "user_score": 1, "username": username},
                initiator_user_id=create_dummy_user.id,
            )
            for hour, username in ((10, "before"), (11, "after"))
        ]
    )
    await test_session.commit()

    response = await request_notification_groups(client, get_test_token)
    [group] = response.json()["list"]

    assert group["count"] == 2
    assert group["actors"] == 1


async def test_notification_groups_split_by_kyiv_day(
    client, create_test_user, get_test_token, test_session
):
    # 21:30 UTC is 23:30 in Kyiv, 22:30 UTC is already the next day there
    test_session.add_all(
        [
            collection_vote(create_test_user, datetime(2026, 11, 7, 21, 30), 1),
            collection_vote(create_test_user, datetime(2026, 11, 7, 22, 30), 1),
        ]
    )
    await test_session.commit()

    response = await request_notification_groups(client, get_test_token)
    references = [group["reference"] for group in response.json()["list"]]

    assert references == [
        "collection_vote:1:2026-11-08",
        "collection_vote:1:2026-11-07",
    ]


async def test_notification_groups_pagination(
    client, create_test_user, get_test_token, test_session
):
    test_session.add_all(
        [hikka_update(create_test_user, at(7, hour)) for hour in range(5)]
    )
    await test_session.commit()

    response = await request_notification_groups(
        client, get_test_token, page=2, size=2
    )

    assert response.json()["pagination"] == {
        "total": 5,
        "pages": 3,
        "page": 2,
    }
    assert len(response.json()["list"]) == 2


async def test_notification_group_seen(
    client,
    create_test_user,
    create_dummy_user,
    get_test_token,
    get_dummy_token,
    test_session,
):
    user = create_test_user
    test_session.add_all(
        [
            collection_vote(user, at(7, 10), 1),
            collection_vote(user, at(7, 11), 1),
            # Older and newer notifications outside the group stay unseen
            hikka_update(user, at(6, 10)),
            hikka_update(user, at(7, 12)),
            collection_vote(create_dummy_user, at(7, 10), 1),
        ]
    )
    await test_session.commit()

    response = await request_notification_group_seen(
        client, "collection_vote:1:2026-11-07", get_test_token
    )
    assert response.status_code == status.HTTP_200_OK

    groups = (await request_notification_groups(client, get_test_token)).json()
    unseen = {group["reference"]: group["unseen"] for group in groups["list"]}

    assert unseen["collection_vote:1:2026-11-07"] == 0
    assert sum(unseen.values()) == 2

    response = await request_notifications_count(client, get_dummy_token)
    assert response.json()["unseen"] == 1


async def test_notification_group_seen_bad_reference(
    client, create_test_user, get_test_token
):
    for reference in ["nope", "unknown_type::2026-11-07", "follow::not-a-day"]:
        response = await request_notification_group_seen(
            client, reference, get_test_token
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
