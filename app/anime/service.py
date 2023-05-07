from app.models import Anime


async def anime_fetch_related(anime: Anime) -> Anime:
    await anime.fetch_related("studios", "producers", "genres")
    return anime
