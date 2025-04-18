from app.models import Anime, Image
from sqlalchemy import select
from app.utils import utcnow
from app import utils


async def save_anime_list(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["poster"] for entry in data]

    cache = await session.scalars(
        select(Anime).filter(Anime.content_id.in_(content_ids))
    )

    anime_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).filter(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_anime = []

    for anime_data in data:
        updated = utils.from_timestamp(anime_data["updated"])
        slug = utils.slugify(anime_data["title_ja"], anime_data["content_id"])

        if anime_data["content_id"] in anime_cache:
            anime = anime_cache[anime_data["content_id"]]

            # TODO: this is temporary solution, eventually we shoud fix that
            # if anime.deleted is False and anime_data["deleted"] is True:
            #     anime.needs_search_update = True
            #     anime.deleted = True
            #     session.add(anime)

            #     await service.create_log(
            #         session,
            #         constants.LOG_CONTENT_DELETED,
            #         None,
            #         anime.id,
            #         {
            #             "content_type": constants.CONTENT_ANIME,
            #         },
            #     )

            #     continue

            if updated == anime.aggregator_updated:
                continue

            if anime.needs_update:
                continue

            anime.needs_update = True

            add_anime.append(anime)

            # print(f"Anime needs update: {anime.title_ja}")

        else:
            # if anime_data["deleted"] is True:
            #     continue

            if not (image := image_cache.get(anime_data["poster"])):
                if anime_data["poster"]:
                    image = Image(
                        **{
                            "path": anime_data["poster"],
                            "created": utcnow(),
                            "uploaded": True,
                            "ignore": False,
                            "system": True,
                        }
                    )

                    image_cache[anime_data["poster"]] = image

            start_date = utils.from_timestamp(anime_data["start_date"])
            end_date = utils.from_timestamp(anime_data["end_date"])

            anime = Anime(
                **{
                    "needs_search_update": True,
                    "episodes_released": anime_data["episodes_released"],
                    "year": start_date.year if start_date else None,
                    "episodes_total": anime_data["episodes_total"],
                    "media_type": anime_data["media_type"],
                    "content_id": anime_data["content_id"],
                    "scored_by": anime_data["scored_by"],
                    "title_en": anime_data["title_en"],
                    "title_ja": anime_data["title_ja"],
                    "title_ua": anime_data["title_ua"],
                    "mal_id": anime_data["mal_id"],
                    "status": anime_data["status"],
                    "season": anime_data["season"],
                    "score": anime_data["score"],
                    "nsfw": anime_data["nsfw"],
                    "start_date": start_date,
                    "image_relation": image,
                    "needs_update": True,
                    "end_date": end_date,
                    "updated": updated,
                    "slug": slug,
                    "stats": {
                        "completed": 0,
                        "watching": 0,
                        "dropped": 0,
                        "on_hold": 0,
                        "planned": 0,
                        "score_1": 0,
                        "score_2": 0,
                        "score_3": 0,
                        "score_4": 0,
                        "score_5": 0,
                        "score_6": 0,
                        "score_7": 0,
                        "score_8": 0,
                        "score_9": 0,
                        "score_10": 0,
                    },
                }
            )

            add_anime.append(anime)

            # print(f"Added anime: {anime.title_ja}")

    session.add_all(add_anime)
    await session.commit()
