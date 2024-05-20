from app.database import sessionmanager
from app.utils import to_timestamp
from sqlalchemy import desc, func
from sqlalchemy import select
from app.models import Anime
import json
import math


async def generate_sitemap(session):
    result = []

    limit = 10000
    total = await session.scalar(
        select(func.count(Anime.id)).filter(
            Anime.deleted == False,  # noqa: E712
        )
    )
    pages = math.ceil(total / limit) + 1

    for page in range(1, pages):
        offset = (limit * (page)) - limit

        data = await session.execute(
            select(Anime.slug, Anime.updated)
            .filter(Anime.deleted == False)  # noqa: E712
            .order_by(
                desc(Anime.score),
                desc(Anime.scored_by),
                desc(Anime.id),
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
    """Generate sitemap file"""

    async with sessionmanager.session() as session:
        with open(
            f"{settings.backend.sitemap_path}/sitemap_anime.json", "w"
        ) as file:
            result = await generate_sitemap(session)
            file.write(json.dumps(result))
