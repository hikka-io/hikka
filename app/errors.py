from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .schemas import CustomModel
from fastapi import Request
from pydantic import Field


class ErrorResponse(CustomModel):
    message: str = Field(examples=["Example error message"])
    code: str = Field(examples=["example_error"])


errors = {
    "auth": {
        "activation-valid": ["Previous activation token still valid", 400],
        "reset-valid": ["Previous password reset token still valid", 400],
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
        "token-expired": ["Token has expired", 400],
        "invalid-code": ["Invalid OAuth code", 400],
        "oauth-error": ["Error during OAuth", 400],
        "user-not-found": ["User not found", 404],
        "email-set": ["Email already set", 400],
        "not-available": ["Signup not available ", 400],
        "invalid-username": ["Invalid username", 400],
    },
    "settings": {
        "username-cooldown": ["Username can be changed once per hour", 400],
        "email-cooldown": ["Email can be changed once per day", 400],
        "username-taken": ["Username already taken", 400],
        "invalid-username": ["Invalid username", 400],
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
    "manga": {
        "unknown-magazine": ["Unknown magazine", 400],
        "unknown-genre": ["Unknown genre", 400],
        "not-found": ["Manga not found", 404],
    },
    "edit": {
        "missing-content-type": ["You must specify content type", 400],
        "not-pending": ["Only pending edit can be changed", 400],
        "moderator-not-found": ["Moderator not found", 404],
        "not-author": ["Only author can modify edit", 400],
        "invalid-content-id": ["Invalid content id", 400],
        "content-not-found": ["Content not found", 404],
        "author-not-found": ["Author not found", 404],
        "bad-edit": ["This edit is invalid", 400],
        "invalid-field": ["Invalid field", 400],
        "not-found": ["Edit not found", 404],
        "empty-edit": ["Empty edit", 400],
    },
    "comment": {
        "rate-limit": ["You have reached comment rate limit, try later", 400],
        "not-editable": ["This comment can't be edited anymore", 400],
        "parent-not-found": ["Parent comment not found", 404],
        "already-hidden": ["Comment is already hidden", 400],
        "not-owner": ["You can't edit this comment", 400],
        "content-not-found": ["Content not found", 404],
        "max-depth": ["Max reply depth reached", 400],
        "empty-markdown": ["Empty markdown", 400],
        "not-found": ["Comment not found", 404],
        "hidden": ["Comment is hidden", 400],
    },
    "studio": {
        "not-found": ["Studio not found", 404],
    },
    "genre": {
        "not-found": ["Genre not found", 404],
    },
    "watch": {
        "empty-random": ["You don't have any watch entries", 400],
        "bad-episodes": ["Bad episodes number provided", 400],
        "not-found": ["Watch record not found", 404],
    },
    "favourite": {
        "exists": ["Favourite record already exists", 400],
        "not-found": ["Favourite record not found", 404],
        "content-not-found": ["Content not found", 404],
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
    "upload": {
        "rate-limit": ["You have reached upload rate limit, try later", 400],
        "not-square": ["Image shoudld be square", 400],
        "bad-resolution": ["Bad resolution", 400],
        "bad-mime": ["Don't be bad mime", 400],
        "bad-size": ["Bad file size", 400],
        "missconfigured-permission": [
            "If you see this, check upload permissions in rate limit",
            400,
        ],
    },
    "notification": {
        "not-found": ["Notification not found", 404],
        "seen": ["Notification already seen", 400],
    },
    "collections": {
        "bad-content-type": ["You can't change collection content type", 400],
        "bad-order-not-consecutive": ["Order must be consecutive", 400],
        "bad-order-duplicated": ["You can't set duplicated order", 400],
        "empty-content-type": ["Content type is not specified", 400],
        "content-limit": ["Collectio content limit violation", 400],
        "limit": ["You have reached collections limit", 400],
        "bad-order-start": ["Order must start from 1", 400],
        "unlabled-content": ["Unlabled content", 400],
        "bad-labels-order": ["Bad labels order", 400],
        "author-not-found": ["Author not found", 404],
        "not-found": ["Collection not found", 404],
        "bad-label": ["Unknown label", 400],
        "bad-content": ["Bad content", 400],
        "moderator-content-update": [
            "Moderator can't update content in collection",
            400,
        ],
    },
    "vote": {
        "content-not-found": ["Content not found", 404],
        "not-found": ["Vote record not found", 404],
    },
    "schedule": {
        "incompatible-filters": ["You've specified incompatible filters", 400],
        "watch-no-user": ["You can't use only_watch without user", 400],
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
    error = exception.errors()[0]

    field_location = error["loc"][0]
    error_message = f"in request {field_location}"

    if len(error["loc"]) > 1:
        field_name = error["loc"][1]
        error_message = f"{field_name} {error_message}"

    error_message = f"Invalid field {error_message}"

    return JSONResponse(
        status_code=400,
        content={
            "code": "system:validation_error",
            "message": error_message.capitalize(),
        },
    )
