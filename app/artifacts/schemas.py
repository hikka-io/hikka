from app.schemas import CustomModel
from app.schemas import datetime_pd


# Args
class PrivateArgs(CustomModel):
    private: bool


# Responses
class ArtifactResponse(CustomModel):
    created: datetime_pd
    updated: datetime_pd
    private: bool
    data: dict
    name: str
