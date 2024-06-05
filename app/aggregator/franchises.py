from app.models import Anime, Manga, Franchise
from sqlalchemy import select
from app import constants
from app import utils


# TODO: optimize it
async def save_franchises_list(session, data):
    content_ids = [entry["content_id"] for entry in data]

    cache = await session.scalars(
        select(Franchise).filter(Franchise.content_id.in_(content_ids))
    )

    franchises_cache = {entry.content_id: entry for entry in cache}

    for franchise_data in data:
        if not (
            franchise := franchises_cache.get(franchise_data["content_id"])
        ):
            franchise = Franchise(content_id=franchise_data["content_id"])

        updated = utils.from_timestamp(franchise_data["updated"])

        if updated == franchise.updated:
            continue

        franchise.scored_by = franchise_data["scored_by"]
        franchise.score = franchise_data["score"]
        franchise.updated = updated

        session.add(franchise)
        await session.commit()

        anime_cache = await session.scalars(
            select(Anime).filter(
                Anime.content_id.in_(
                    [
                        entry["content_id"]
                        for entry in franchise_data["franchise_entries"]
                        if entry["content_type"] == constants.CONTENT_ANIME
                    ]
                )
            )
        )

        manga_cache = await session.scalars(
            select(Manga).filter(
                Manga.content_id.in_(
                    [
                        entry["content_id"]
                        for entry in franchise_data["franchise_entries"]
                        if entry["content_type"] == constants.CONTENT_MANGA
                    ]
                )
            )
        )

        update_content = []

        for anime in anime_cache:
            anime.franchise_relation = franchise
            update_content.append(anime)

        for manga in manga_cache:
            manga.franchise_relation = franchise
            update_content.append(manga)

        session.add_all(update_content)

        print(f"Processed franchise {franchise.content_id}")

    await session.commit()
