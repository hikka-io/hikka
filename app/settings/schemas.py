from app.schemas import CustomModel, CustomModelExtraIgnore
from pydantic import Field
from enum import Enum


# Enums
class ImportWatchStatusEnum(str, Enum):
    completed = "Completed"
    watching = "Watching"
    planned = "Plan to Watch"
    on_hold = "On-Hold"
    dropped = "Dropped"


# Args
class DescriptionArgs(CustomModel):
    description: str | None = Field(
        default=None, max_length=140, examples=["Hikka"]
    )


class ImportAnimeArgs(CustomModelExtraIgnore):
    series_animedb_id: int = Field(ge=0, le=1000000)
    my_watched_episodes: int = Field(ge=0, le=10000)
    my_comments: str | dict = Field(max_length=1024)
    my_times_watched: int = Field(default=0, ge=0)
    my_score: int = Field(default=0, ge=0, le=10)
    my_status: ImportWatchStatusEnum


class ImportAnimeListArgs(CustomModelExtraIgnore):
    anime: list[ImportAnimeArgs]
    overwrite: bool
