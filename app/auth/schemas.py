from pydantic import BaseModel, EmailStr, Field
from ..utils import Datetime


# Args
class SignupArgs(BaseModel):
    username: str = Field(max_length=64, regex="[A-Za-z0-9]")
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr


class LoginArgs(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr


class ComfirmResetArgs(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    token: str


# Responses
class UserResponse(BaseModel):
    created: Datetime
    username: str


class TokenResponse(BaseModel):
    expiration: Datetime
    created: Datetime
    secret: str
