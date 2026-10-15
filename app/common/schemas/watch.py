from app.schemas import CustomModel, datetime_pd
from pydantic import Field
from app import constants
from enum import Enum


# Enums
class WatchStatusEnum(str, Enum):
    completed = constants.WATCH_COMPLETED
    watching = constants.WATCH_WATCHING
    planned = constants.WATCH_PLANNED
    on_hold = constants.WATCH_ON_HOLD
    dropped = constants.WATCH_DROPPED


# Responses
class WatchResponseBase(CustomModel):
    reference: str = Field(examples=["c773d0bf-1c42-4c18-aec8-1bdd8cb0a434"])
    note: str | None = Field(max_length=2048, examples=["🤯"])
    updated: datetime_pd = Field(examples=[1686088809])
    created: datetime_pd = Field(examples=[1686088809])
    status: str = Field(examples=["watching"])
    rewatches: int = Field(examples=[2])
    duration: int = Field(examples=[24])
    episodes: int = Field(examples=[3])
    score: int = Field(examples=[8])
    start_date: datetime_pd | None
    end_date: datetime_pd | None
