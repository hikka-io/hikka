from meilisearch_python_async.models.settings import MeilisearchSettings
from meilisearch_python_async import Client
from app.utils import get_season
from tortoise.queryset import Q
from tortoise import Tortoise
from app.models import Anime
import config


async def meilisearch_settings():
    print("Meilisearch: Updating settings")

    async with Client(
        config.meilisearch["endpoint"], config.meilisearch["token"]
    ) as client:
        index = client.index("content_anime")

        await index.update_settings(
            MeilisearchSettings(
                filterable_attributes=[
                    "media_type",
                    "producers",
                    "episodes",
                    "studios",
                    "rating",
                    "season",
                    "genres",
                    "status",
                    "source",
                    "score",
                    "year",
                ],
                searchable_attributes=[
                    "title_ua",
                    "title_en",
                    "title_ja",
                    "synonyms",
                ],
                sortable_attributes=[
                    "scored_by",
                    "score",
                    "year",
                ],
                displayed_attributes=[
                    "media_type",
                    "title_ua",
                    "title_en",
                    "title_ja",
                    "score",
                    "slug",
                    # "scored_by",
                    # "producers",
                    # "studios",
                    # "rating",
                    # "season",
                    # "status",
                    # "source",
                    # "synonyms",
                    # "genres",
                    # "episodes",
                    # "year",
                    # "image",
                ],
                distinct_attribute="slug",
            )
        )


async def meilisearch_populate():
    print("Meilisearch: Populating database")

    anime_list = await Anime.filter(~Q(media_type=None)).prefetch_related(
        "genres", "studios", "producers"
    )

    documents = []

    for anime in anime_list:
        documents.append(
            {
                "year": anime.start_date.year if anime.start_date else None,
                "producers": [company.slug for company in anime.producers],
                "studios": [company.slug for company in anime.studios],
                "genres": [genre.slug for genre in anime.genres],
                "season": get_season(anime.start_date),
                "media_type": anime.media_type,
                "scored_by": anime.scored_by,
                "synonyms": anime.synonyms,
                "episodes": anime.episodes,
                "title_ua": anime.title_ua,
                "title_en": anime.title_en,
                "title_ja": anime.title_ja,
                "status": anime.status,
                "source": anime.source,
                "rating": anime.rating,
                "id": anime.content_id,
                "score": anime.score,
                "slug": anime.slug,
            }
        )

        print(f"Meilisearch: Updated anime {anime.title_ja}")

    async with Client(
        config.meilisearch["endpoint"], config.meilisearch["token"]
    ) as client:
        index = client.index("content_anime")

        await index.add_documents(documents)


async def update_search():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    await meilisearch_settings()
    await meilisearch_populate()
