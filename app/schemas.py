from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from datetime import datetime
from . import utils
import orjson


# Custom Pydantic model
class ORJSONModel(BaseModel):
    class Config:
        json_encoders = {datetime: utils.to_timestamp}
        json_dumps = utils.orjson_dumps
        json_loads = orjson.loads
        orm_mode = True

    def serializable_dict(self, **kwargs):
        default_dict = super().dict(**kwargs)
        return jsonable_encoder(default_dict)


# Args
class PaginationArgs(ORJSONModel):
    page: int = Field(default=1, gt=0)


# Responses
class PaginationResponse(ORJSONModel):
    total: int
    pages: int
    page: int
