from pydantic import EmailStr, Field
from app.schemas import ORJSONModel
from datetime import datetime


# Args
class SignupArgs(ORJSONModel):
    username: str = Field(max_length=64, regex="[A-Za-z0-9]")
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr


class LoginArgs(ORJSONModel):
    password: str = Field(min_length=8, max_length=64)
    email: EmailStr


class ComfirmResetArgs(ORJSONModel):
    password: str = Field(min_length=8, max_length=64)
    token: str


# Responses
class UserResponse(ORJSONModel):
    created: datetime
    username: str


class TokenResponse(ORJSONModel):
    expiration: datetime
    created: datetime
    secret: str
