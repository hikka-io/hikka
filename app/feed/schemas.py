from app.schemas import CustomModel
from datetime import datetime
from typing import Literal
from app import constants


# Args
class FeedArgs(CustomModel):
    before: datetime | None = None
    content_type: (
        Literal[
            constants.CONTENT_COLLECTION,
            constants.CONTENT_ARTICLE,
            constants.CONTENT_COMMENT,
        ]
        | None
    ) = None
