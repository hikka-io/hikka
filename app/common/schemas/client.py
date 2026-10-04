from app.common.schemas.user import UserResponse
from app.schemas import CustomModel, datetime_pd


class ClientResponse(CustomModel):
    created: datetime_pd
    updated: datetime_pd
    user: UserResponse
    description: str
    reference: str
    verified: bool
    name: str
