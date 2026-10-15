from app.schemas import CustomModel, datetime_pd
from pydantic import Field
from enum import Enum


# Enums
class UserLinkIconEnum(str, Enum):
    instagram = "instagram"
    mangainua = "mangainua"
    mangalist = "mangalist"
    telegram = "telegram"
    threads = "threads"
    twitter = "twitter"
    discord = "discord"
    bluesky = "bluesky"
    anitube = "anitube"
    dgmanga = "dgmanga"
    youtube = "youtube"
    github = "github"
    custom = "custom"
    reddit = "reddit"
    steam = "steam"
    mikai = "mikai"
    zenko = "zenko"
    chess = "chess"


# Responses
class UserLinkResponse(CustomModel):
    url: str = Field(examples=["https://github.com/hikka-io"])
    text: str | None = Field(examples=["GitHub"])
    icon: UserLinkIconEnum


class UserResponse(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    updated: datetime_pd | None = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    description: str | None = Field(examples=["Hikka"])
    username: str | None = Field(examples=["hikka"])
    links: list[UserLinkResponse]
    cover: str | None
    active: bool
    avatar: str
    role: str


class FollowUserResponse(UserResponse):
    is_followed: bool
