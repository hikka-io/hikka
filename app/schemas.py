from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from datetime import datetime
from . import constants
from enum import Enum
from . import utils
import orjson


# Custom Pydantic model
class ORJSONModel(BaseModel):
    class Config:
        json_encoders = {datetime: utils.to_timestamp}
        json_dumps = utils.orjson_dumps
        json_loads = orjson.loads
        use_enum_values = True
        orm_mode = True

    def serializable_dict(self, **kwargs):
        default_dict = super().dict(**kwargs)
        return jsonable_encoder(default_dict)


# Enums
class WatchStatusEnum(str, Enum):
    planned = constants.WATCH_PLANNED
    watching = constants.WATCH_WATCHING
    completed = constants.WATCH_COMPLETED
    on_hold = constants.WATCH_ON_HOLD
    dropped = constants.WATCH_DROPPED


# Args
class PaginationArgs(ORJSONModel):
    page: int = Field(default=1, gt=0)


# Responses
class PaginationResponse(ORJSONModel):
    total: int
    pages: int
    page: int
