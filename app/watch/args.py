from ..constants import WATCH, WATCH_PLANNED
from pydantic import BaseModel, Field
from typing import Union

class WatchArgs(BaseModel):
    user_score: int = Field(default=1, ge=1, le=10)
    episodes: int = Field(default=0, ge=0)
    note: Union[str, None] = None

    status: str = Field(
        default=WATCH_PLANNED, regex="|".join(WATCH)
    )
