from app.schemas import PaginationResponse, CustomModel, UserResponse
from app.schemas import datetime_pd
from app import constants
from enum import Enum


# Enums
class NotificationTypeEnum(str, Enum):
    comment_reply = constants.NOTIFICATION_COMMENT_REPLY
    comment_vote = constants.NOTIFICATION_COMMENT_VOTE
    comment_tag = constants.NOTIFICATION_COMMENT_TAG
    collection_comment = constants.NOTIFICATION_COLLECTION_COMMENT
    article_comment = constants.NOTIFICATION_ARTICLE_COMMENT
    collection_vote = constants.NOTIFICATION_COLLECTION_VOTE
    article_vote = constants.NOTIFICATION_ARTICLE_VOTE
    edit_comment = constants.NOTIFICATION_EDIT_COMMENT
    edit_accepted = constants.NOTIFICATION_EDIT_ACCEPTED
    edit_denied = constants.NOTIFICATION_EDIT_DENIED
    edit_updated = constants.NOTIFICATION_EDIT_UPDATED
    hikka_update = constants.NOTIFICATION_HIKKA_UPDATE
    schedule_anime = constants.NOTIFICATION_SCHEDULE_ANIME
    follow = constants.NOTIFICATION_FOLLOW
    thirdparty_login = constants.NOTIFICATION_THIRDPARTY_LOGIN


# Responses
class NotificationResponse(CustomModel):
    initiator_user: UserResponse | None
    notification_type: NotificationTypeEnum
    created: datetime_pd
    reference: str
    seen: bool
    data: dict


class NotificationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationResponse]


class NotificationUnseenResponse(CustomModel):
    unseen: int
