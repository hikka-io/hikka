from app.schemas import CustomModel
from app.schemas import datetime_pd


# Args
class PrivateArgs(CustomModel):
    private: bool


# Responses
class DigestPrivacyResponse(CustomModel):
    private: bool


class DigestResponse(DigestPrivacyResponse):
    created: datetime_pd
    updated: datetime_pd
    data: dict
    name: str
