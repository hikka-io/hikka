from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .schemas import ORJSONModel
from fastapi import Request
from pydantic import Field


class ErrorResponse(ORJSONModel):
    message: str = Field(example="Example error message")
    code: str = Field(example="example_error")


errors = {
    "auth": {
        "username-required": ["Username is required to do that action", 400],
        "activation-valid": ["Previous activation token still valid", 400],
        "reset-valid": ["Previous password reset token still valid", 400],
        "email-required": ["Email is required to do that action", 400],
        "email-exists": ["User with that email already exists", 400],
        "activation-expired": ["Activation token has expired", 400],
        "activation-invalid": ["Activation token is invalid", 400],
        "oauth-code-required": ["OAuth code required", 400],
        "invalid-provider": ["Invalid OAuth provider", 400],
        "username-taken": ["Username already taken", 400],
        "reset-expired": ["Reset token has expired", 400],
        "reset-invalid": ["Reset token is invalid", 400],
        "already-activated": ["Already activated", 400],
        "invalid-token": ["Auth token is invalid", 400],
        "missing-token": ["Auth token is missing", 400],
        "invalid-password": ["Invalid password", 400],
        "username-set": ["Username already set", 400],
        "not-activated": ["User not activated", 400],
        "token-expired": ["Token has expired", 400],
        "invalid-code": ["Invalid OAuth code", 400],
        "oauth-error": ["Error during OAuth", 400],
        "user-not-found": ["User not found", 404],
        "email-set": ["Email already set", 400],
        "not-available": ["Signup not available ", 400],
    },
    "permission": {
        "denied": ["You don't have permission for this action", 403],
    },
    "anime": {
        "no-franchise": ["This anime doesn't have franchise", 400],
        "unknown-producer": ["Unknown producer", 400],
        "unknown-studio": ["Unknown studio", 400],
        "bad-year": ["Invalid years passed", 400],
        "unknown-genre": ["Unknown genre", 400],
        "not-found": ["Anime not found", 404],
    },
    "edit": {
        "not-pending": ["Only pending edit can be changed", 400],
        "invalid-content-id": ["Invalid content id", 400],
        "wrong-content-type": ["Wrong content type", 400],
        "not-author": ["Only author can modify edit", 400],
        "content-not-found": ["Content not found", 404],
        "empty-edit": ["This edit is empty", 400],
        "bad-edit": ["This edit is invalid", 400],
        "invalid-field": ["Invalid field", 400],
        "not-found": ["Edit not found", 404],
    },
    "studio": {
        "not-found": ["Studio not found", 404],
    },
    "genre": {
        "not-found": ["Genre not found", 404],
    },
    "watch": {
        "bad-episodes": ["Bad episodes number provided", 400],
        "not-found": ["Watch record not found", 404],
    },
    "favourite": {
        "exists": ["Favourite record for this anime already exists", 400],
        "not-found": ["Favourite record not found", 404],
    },
    "captcha": {
        "invalid": ["Failed to validate captcha", 401],
    },
    "user": {
        "not-found": ["User not found", 404],
    },
    "follow": {
        "already-following": ["This user is already followed", 400],
        "not-following": ["This user is not followed", 400],
        "invalid-action": ["Invalid action", 401],
        "self": ["Can't follow self", 400],
    },
    "search": {
        "query-down": ["Search by query unavailable at the moment", 400],
    },
    "company": {
        "not-found": ["Company not found", 404],
    },
    "character": {
        "not-found": ["Character not found", 404],
    },
    "person": {
        "not-found": ["Person not found", 404],
    },
}


class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message


def build_error_code(scope: str, message: str):
    return scope.replace("-", "_") + ":" + message.replace("-", "_")


async def abort_handler(request: Request, exception: Abort):
    error_code = build_error_code(exception.scope, exception.message)

    try:
        error_message = errors[exception.scope][exception.message][0]
        status_code = errors[exception.scope][exception.message][1]
    except Exception:
        error_message = "Unknown error"
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={
            "message": error_message,
            "code": error_code,
        },
    )


async def validation_handler(
    request: Request, exception: RequestValidationError
):
    error_message = str(exception).replace("\n", " ").replace("   ", " ")
    return JSONResponse(
        status_code=400,
        content={
            "code": "system:validation_error",
            "message": error_message,
        },
    )
