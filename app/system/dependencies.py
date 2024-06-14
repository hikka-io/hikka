from app.utils import get_settings
from app.errors import Abort
from typing import Annotated
from fastapi import Header


async def validate_backup_token(
    backup_token: Annotated[str, Header(alias="auth")]
) -> str:
    settings = get_settings()

    if backup_token != settings.backup.token:
        raise Abort("system", "bad-backup-token")

    return True
