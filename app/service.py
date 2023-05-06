from .models import User, AuthToken, Anime
from typing import Union


async def get_user_by_username(username: str) -> Union[User, None]:
    return await User.filter(username=username).first()


async def get_anime_by_slug(slug: str) -> Union[Anime, None]:
    return await Anime.filter(slug=slug).first()


async def get_auth_token(secret: str) -> Union[AuthToken, None]:
    return (
        await AuthToken.filter(
            secret=secret,
        )
        .prefetch_related("user")
        .first()
    )
