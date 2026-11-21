from sqlalchemy import Date, Integer, String, case, cast, func, literal, select
from sqlalchemy.sql.elements import ColumnElement
from app.models import Notification, User
from app import constants


GROUP_TIMEZONE = "Europe/Kyiv"

# Members returned per group; `count` still reports the full size.
GROUP_NOTIFICATIONS_LIMIT = 50

VOTE_TYPES = [
    constants.NOTIFICATION_COMMENT_VOTE,
    constants.NOTIFICATION_COLLECTION_VOTE,
    constants.NOTIFICATION_ARTICLE_VOTE,
]

EDIT_TYPES = [
    constants.NOTIFICATION_EDIT_ACCEPTED,
    constants.NOTIFICATION_EDIT_DENIED,
    constants.NOTIFICATION_EDIT_UPDATED,
]

data = Notification.data
notification_type = Notification.notification_type


def group_subkey() -> ColumnElement[str]:
    return func.coalesce(
        case(
            (
                notification_type.in_(VOTE_TYPES),
                cast(
                    func.sign(cast(data["user_score"].astext, Integer)),
                    String,
                ),
            ),
            (
                notification_type == constants.NOTIFICATION_SCHEDULE_ANIME,
                data["slug"].astext,
            ),
            (
                notification_type == constants.NOTIFICATION_THIRDPARTY_LOGIN,
                data["client"]["reference"].astext,
            ),
            (
                notification_type == constants.NOTIFICATION_HIKKA_UPDATE,
                cast(Notification.id, String),
            ),
            else_=literal(""),
        ),
        literal(""),
    )


def group_day() -> ColumnElement:
    # `created` is naive UTC: tag it as UTC, then take the wall-clock date in Kyiv.
    return cast(
        func.timezone(
            GROUP_TIMEZONE, func.timezone("UTC", Notification.created)
        ),
        Date,
    )


def group_actor() -> ColumnElement[str | None]:
    """Who triggered a member, as a stable account id so renames do not split it.

    Rows older than `initiator_user_id` only store a username: resolve it to the account
    that holds it now, else count the stored handle. Downvotes are anonymous and add no
    actors, even older rows that still store the voter.
    """

    stored_username = data["username"].astext
    legacy_user_id = (
        select(User.id)
        .where(User.username == stored_username)
        .limit(1)
        .scalar_subquery()
    )

    return case(
        (
            notification_type.in_(VOTE_TYPES)
            & (cast(data["user_score"].astext, Integer) < 0),
            None,
        ),
        # COALESCE stops at the first non-null, so new rows skip the lookup
        else_=func.coalesce(
            cast(Notification.initiator_user_id, String),
            cast(legacy_user_id, String),
            stored_username,
        ),
    )


def group_target() -> ColumnElement[str | None]:
    """What a member points at, so a group can say "your 3 comments" vs "your comment".

    Replies have no target: their data names the thread root, not the replied-to comment.
    """

    return case(
        (
            notification_type.in_(
                [
                    constants.NOTIFICATION_COMMENT_VOTE,
                    constants.NOTIFICATION_COMMENT_TAG,
                ]
            ),
            data["comment_reference"].astext,
        ),
        (
            notification_type.in_(
                [
                    constants.NOTIFICATION_COLLECTION_VOTE,
                    constants.NOTIFICATION_ARTICLE_VOTE,
                    constants.NOTIFICATION_SCHEDULE_ANIME,
                ]
            ),
            data["slug"].astext,
        ),
        (notification_type.in_(EDIT_TYPES), data["edit_id"].astext),
        else_=None,
    )


def make_group_reference(notification_type: str, subkey: str, day) -> str:
    return f"{notification_type}:{subkey}:{day.isoformat()}"


def parse_group_reference(reference: str) -> tuple[str, str, str] | None:
    """Splits a reference into type, sub-key and ISO day, or returns None if malformed."""

    head, sep, day = reference.rpartition(":")
    notification_type, sep2, subkey = head.partition(":")
    if not sep or not sep2:
        return None
    if notification_type not in constants.NOTIFICATION_TYPES:
        return None
    return notification_type, subkey, day
