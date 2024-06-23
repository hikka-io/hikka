from app.models import Anime, Manga, Novel
from app.database import sessionmanager
from app.utils import get_settings
from app.utils import to_timestamp
from sqlalchemy import desc, func
from sqlalchemy import select
from app import constants
import json
import math


async def generate_sitemap(session, content_type):
    model = {
        constants.CONTENT_ANIME: Anime,
        constants.CONTENT_MANGA: Manga,
        constants.CONTENT_NOVEL: Novel,
    }.get(content_type)

    result = []

    limit = 10000
    total = await session.scalar(
        select(func.count(model.id)).filter(
            model.deleted == False,  # noqa: E712
        )
    )
    pages = math.ceil(total / limit) + 1

    for page in range(1, pages):
        offset = (limit * (page)) - limit

        data = await session.execute(
            select(model.slug, model.updated)
            .filter(model.deleted == False)  # noqa: E712
            .order_by(
                desc(model.score),
                desc(model.scored_by),
                desc(model.id),
            )
            .limit(limit)
            .offset(offset)
        )

        for entry in data:
            result.append(
                {
                    "updated_at": to_timestamp(entry[1]),
                    "slug": entry[0],
                }
            )

    return result


async def update_sitemap():
    """Generate sitemap files"""

    settings = get_settings()

    async with sessionmanager.session() as session:
        with open(
            f"{settings.backend.sitemap_path}/sitemap_anime.json", "w"
        ) as file:
            result = await generate_sitemap(session, constants.CONTENT_ANIME)
            file.write(json.dumps(result))

        with open(
            f"{settings.backend.sitemap_path}/sitemap_manga.json", "w"
        ) as file:
            result = await generate_sitemap(session, constants.CONTENT_MANGA)
            file.write(json.dumps(result))

        with open(
            f"{settings.backend.sitemap_path}/sitemap_novel.json", "w"
        ) as file:
            result = await generate_sitemap(session, constants.CONTENT_NOVEL)
            file.write(json.dumps(result))
