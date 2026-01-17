from app.utils import get_settings, chunkify
from app.database import sessionmanager
from app.models import Article
from sqlalchemy import select
import aiohttp


async def update_article_views():
    settings = get_settings()

    async with sessionmanager.session() as session:
        slugs = await session.scalars(
            select(Article.slug).filter(
                Article.deleted == False,  # noqa: E712
                Article.draft == False,  # noqa: E712
            )
        )

        headers = {
            "Authorization": f"Bearer {settings.backend.plausible_token}",
            "Content-Type": "application/json",
        }

        for slugs_chunk in chunkify(
            [f"/articles/{slug}" for slug in slugs.fetchall()], 5000
        ):
            async with aiohttp.ClientSession(headers=headers) as aio_session:
                async with aio_session.post(
                    f"{settings.backend.plausible}/api/v2/query",
                    json={
                        "filters": [["is", "event:page", slugs_chunk]],
                        "dimensions": ["event:page"],
                        "metrics": ["visitors"],
                        "site_id": "hikka.io",
                        "date_range": "all",
                    },
                ) as response:
                    content = await response.json()

                    # Sometimes Plausible don't return result
                    # so we need to handle it
                    if "results" not in content:
                        continue

                    plausible_slugs = []
                    plausible_views = {}

                    for page_views in content["results"]:
                        page_slug = page_views["dimensions"][0].split("/")[-1]
                        plausible_views[page_slug] = page_views["metrics"][0]
                        plausible_slugs.append(page_slug)

                    articles = await session.scalars(
                        select(Article).filter(
                            Article.slug.in_(plausible_slugs)
                        )
                    )

                    for article in articles.unique():
                        if not (views := plausible_views.get(article.slug)):
                            continue

                        article.views = views

                        if not session.is_modified(article):
                            continue

                        print(
                            f"Set {article.views} views for artiles {article.title}"
                        )

                    await session.commit()
