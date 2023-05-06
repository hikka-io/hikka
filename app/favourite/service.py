from app.models import AnimeFavourite, Anime, User
from datetime import datetime


async def get_anime_favourite(anime: AnimeFavourite, user: User):
    return await AnimeFavourite.filter(anime=anime, user=user).first()


async def create_anime_favourite(anime: Anime, user: User) -> AnimeFavourite:
    return await AnimeFavourite.create(
        **{
            "created": datetime.utcnow(),
            "anime": anime,
            "user": user,
        }
    )


async def delete_anime_favourite(favourite: AnimeFavourite):
    await favourite.delete()
