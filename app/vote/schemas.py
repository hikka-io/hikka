from app.schemas import CustomModel
from pydantic import Field
from app import constants
from enum import Enum


# Enums
class ContentTypeEnum(str, Enum):
    content_collection = constants.CONTENT_COLLECTION
    content_comment = constants.CONTENT_COMMENT
    content_article = constants.CONTENT_ARTICLE


# Args
class VoteArgs(CustomModel):
    score: int = Field(ge=-1, le=1)


# Responses
class VoteResponse(CustomModel):
    score: int
