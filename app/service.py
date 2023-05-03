from .models import User, AuthToken


async def get_user_by_username(username: str):
    return await User.filter(username=username).first()


async def get_user_by_auth(secret: str) -> User:
    return (
        await AuthToken.filter(
            secret=secret,
        )
        .prefetch_related("user")
        .first()
    )
