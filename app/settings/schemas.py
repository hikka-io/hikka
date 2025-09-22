from app.schemas import CustomModel, CustomModelExtraIgnore, datetime_pd
from pydantic import Field, field_validator, AliasChoices
from app import constants
from enum import Enum


# Enums
class ImportWatchStatusEnum(str, Enum):
    completed = "Completed"
    watching = "Watching"
    planned = "Plan to Watch"
    on_hold = "On-Hold"
    dropped = "Dropped"


class ImportReadStatusEnum(str, Enum):
    completed = "Completed"
    reading = "Reading"
    planned = "Plan to Read"
    on_hold = "On-Hold"
    dropped = "Dropped"


class ImageTypeEnum(str, Enum):
    avatar = constants.UPLOAD_AVATAR
    cover = constants.UPLOAD_COVER


class ReadDeleteContenType(str, Enum):
    manga = constants.CONTENT_MANGA
    novel = constants.CONTENT_NOVEL


# Args
class IgnoredNotificationsArgs(CustomModel):
    ignored_notifications: list[str]

    @field_validator("ignored_notifications")
    def validate_sort(cls, ignored_notifications):
        if len(set(ignored_notifications)) != len(ignored_notifications):
            raise ValueError("Duplicated notification type")

        if any(
            notification_type not in constants.NOTIFICATION_TYPES
            for notification_type in ignored_notifications
        ):
            raise ValueError("Unknown notification type")

        return ignored_notifications


class DescriptionArgs(CustomModel):
    description: str | None = Field(
        default=None, max_length=140, examples=["Hikka"]
    )

    @field_validator("description")
    def validate_description(cls, description):
        return description.strip("\n") if description else description


class ImportWatchArgs(CustomModelExtraIgnore):
    series_animedb_id: int = Field(ge=0, le=1000000)
    my_watched_episodes: int = Field(ge=0, le=10000)
    my_times_watched: int = Field(default=0, ge=0)
    my_score: int = Field(default=0, ge=0, le=10)
    my_status: ImportWatchStatusEnum
    my_comments: str | dict


class ImportReadArgs(CustomModelExtraIgnore):
    manga_mangadb_id: int = Field(ge=0, le=1000000)
    my_read_chapters: int = Field(ge=0, le=10000)
    my_read_volumes: int = Field(ge=0, le=10000)
    my_score: int = Field(ge=0, le=10)
    my_status: ImportReadStatusEnum
    my_comments: str | dict
    my_times_read: int = Field(
        ge=0,
        validation_alias=AliasChoices(
            "my_times_read",
            "my_times_watched",
        ),
    )


class ImportWatchListArgs(CustomModelExtraIgnore):
    anime: list[ImportWatchArgs]
    overwrite: bool


class ImportReadListArgs(CustomModelExtraIgnore):
    content: list[ImportReadArgs]
    overwrite: bool


# Responses
class IgnoredNotificationsResponse(CustomModel):
    ignored_notifications: list[str]


class UserExportWatchResponse(CustomModel):
    note: str | None
    hikka_slug: str
    rewatches: int
    episodes: int
    created: int
    updated: int
    mal_id: int
    status: str
    score: int


class UserExportReadResponse(CustomModel):
    note: str | None
    hikka_slug: str
    chapters: int
    rereads: int
    volumes: int
    created: int
    updated: int
    mal_id: int
    status: str
    score: int


class UserExportResponse(CustomModel):
    anime: list[UserExportWatchResponse]
    manga: list[UserExportReadResponse]
    novel: list[UserExportReadResponse]
    created: datetime_pd
    updated: datetime_pd
