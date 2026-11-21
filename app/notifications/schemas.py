from app.schemas import PaginationResponse, CustomModel, datetime_pd
from app.common.schemas.user import UserResponse
from pydantic import Field, model_validator
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


VOTE_NOTIFICATION_TYPES = (
    constants.NOTIFICATION_COMMENT_VOTE,
    constants.NOTIFICATION_COLLECTION_VOTE,
    constants.NOTIFICATION_ARTICLE_VOTE,
)


# Responses
class NotificationResponse(CustomModel):
    notification_type: NotificationTypeEnum
    initiator_user: UserResponse | None
    created: datetime_pd
    reference: str
    seen: bool
    data: dict

    @model_validator(mode="after")
    def hide_downvoter(self):
        # Downvotes are anonymous; rows older than that rule still store the voter
        if (
            self.notification_type in VOTE_NOTIFICATION_TYPES
            and (self.data.get("user_score") or 0) < 0
        ):
            self.initiator_user = None
            self.data = {
                key: value
                for key, value in self.data.items()
                if key not in ("username", "avatar")
            }

        return self


class NotificationPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationResponse]


class NotificationUnseenResponse(CustomModel):
    unseen: int


class NotificationGroupResponse(CustomModel):
    reference: str = Field(
        description="Stable group key; pass it to mark the group as seen",
        examples=["collection_vote:1:2026-11-07"],
    )
    notification_type: NotificationTypeEnum
    created: datetime_pd = Field(description="Newest member's creation time")
    count: int = Field(description="Members in the group")
    unseen: int = Field(description="Members not seen yet")
    actors: int = Field(description="Distinct users behind the members")
    targets: int = Field(
        description="Distinct things the members point at (comments, edits, collections, ...)"
    )
    notifications: list[NotificationResponse] = Field(
        description="Newest members first, up to 50"
    )


class NotificationGroupPaginationResponse(CustomModel):
    pagination: PaginationResponse
    list: list[NotificationGroupResponse]
