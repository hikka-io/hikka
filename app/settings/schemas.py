from app.schemas import CustomModel, CustomModelExtraIgnore
from pydantic import Field, field_validator
from app import constants
from enum import Enum


# Enums
class ImportWatchStatusEnum(str, Enum):
    completed = "Completed"
    watching = "Watching"
    planned = "Plan to Watch"
    on_hold = "On-Hold"
    dropped = "Dropped"


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


class ImportAnimeArgs(CustomModelExtraIgnore):
    series_animedb_id: int = Field(ge=0, le=1000000)
    my_watched_episodes: int = Field(ge=0, le=10000)
    my_times_watched: int = Field(default=0, ge=0)
    my_score: int = Field(default=0, ge=0, le=10)
    my_status: ImportWatchStatusEnum
    my_comments: str | dict


class ImportAnimeListArgs(CustomModelExtraIgnore):
    anime: list[ImportAnimeArgs]
    overwrite: bool


# Responses
class IgnoredNotificationsResponse(CustomModel):
    ignored_notifications: list[str]
