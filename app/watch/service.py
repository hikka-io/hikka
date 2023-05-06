from app.models import AnimeWatch, Anime, User
from .schemas import WatchArgs
from datetime import datetime


async def get_anime_watch(anime: Anime, user: User):
    return await AnimeWatch.filter(anime=anime, user=user).first()


# ToDo: rewrite this function?
async def save_watch(anime: Anime, user: User, args: WatchArgs):
    # Create watch record if missing
    if not (watch := await AnimeWatch.filter(anime=anime, user=user).first()):
        watch = AnimeWatch()
        watch.created = datetime.utcnow()
        watch.anime = anime
        watch.user = user

    # Set attributes from args to watch record
    for key, value in args.dict().items():
        setattr(watch, key, value)

    # Save watch record
    watch.updated = datetime.utcnow()
    await watch.save()

    return watch


async def delete_watch(watch: AnimeWatch):
    await watch.delete()
