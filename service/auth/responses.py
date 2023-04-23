from pydantic import BaseModel
from ..utils import Datetime

class UserResponse(BaseModel):
    created: Datetime
    activated: bool
    username: str

class TokenResponse(BaseModel):
    expiration: Datetime
    created: Datetime
    secret: str
