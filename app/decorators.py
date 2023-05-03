from datetime import datetime, timedelta
from .models import AuthToken
from fastapi import Header
from .errors import Abort
from .models import User

# Check auth
def auth_required(permissions: list = []):
    async def auth(
        auth: str = Header()
    ) -> User:
        token = await AuthToken.filter(
            secret=auth
        ).prefetch_related("user").first()

        if not token:
            raise Abort("auth", "invalid-token")

        if not token.user:
            raise Abort("auth", "user-not-found")

        if token.user.banned:
            raise Abort("auth", "banned")

        now = datetime.utcnow()

        if now > token.expiration:
            raise Abort("auth", "token-expired")

        # Check required permissions
        # if len(permissions) > 0:
        #     role = await token.user.role
        #     for permission_name in permissions:
        #         if not (await role.permissions.filter(
        #             name=permission_name
        #         ).first()):
        #             raise Abort("permission", "missing")

        token.expiration = now + timedelta(days=1)
        await token.save()

        return token.user

    return auth
