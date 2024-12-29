from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from app.utils import get_settings
from sqlalchemy import select
from app.models import Anime
import asyncio
import json


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        result = []

        anime_list = await session.scalars(
            select(Anime)
            .filter(Anime.external.op("@>")([{"text": "Toloka"}]))
            .options(joinedload(Anime.genres))
            .order_by(Anime.score.desc())
        )

        for anime in anime_list.unique().all():
            result.append(
                {
                    "genres": [genre.name_ua for genre in anime.genres],
                    "description": anime.synopsis_ua,
                    "title_ua": anime.title_ua,
                    "title_en": anime.title_en,
                    "title_ja": anime.title_ja,
                    "score": anime.score,
                    "image": anime.image,
                    "hikka": f"https://hikka.io/anime/{anime.slug}",
                    "toloka": [
                        url["url"]
                        for url in anime.external
                        if url["text"] == "Toloka"
                    ],
                }
            )

        with open("export.json", "w") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
