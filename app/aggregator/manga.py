from app.models import Manga, Image
from sqlalchemy import select
from app.utils import utcnow
from app import utils


async def save_manga_list(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["poster"] for entry in data]

    cache = await session.scalars(
        select(Manga).filter(Manga.content_id.in_(content_ids))
    )

    manga_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).filter(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_manga = []

    for manga_data in data:
        slug = utils.slugify(manga_data["title_ja"], manga_data["content_id"])
        created = utils.from_timestamp(manga_data["created"])
        updated = utils.from_timestamp(manga_data["updated"])

        if manga_data["content_id"] in manga_cache:
            manga = manga_cache[manga_data["content_id"]]

            # TODO: this is temporary solution, eventually we shoud fix that
            # if manga.deleted is False and manga_data["deleted"] is True:
            #     manga.needs_search_update = True
            #     manga.deleted = True
            #     session.add(manga)

            #     await service.create_log(
            #         session,
            #         constants.LOG_CONTENT_DELETED,
            #         None,
            #         manga.id,
            #         {
            #             "content_type": constants.CONTENT_MANGA,
            #         },
            #     )

            #     continue

            if manga.created is None:
                manga.created = created

            if updated == manga.aggregator_updated:
                continue

            if manga.needs_update:
                continue

            manga.needs_update = True

            # print(f"Manga needs update: {manga.title_original}")

        else:
            # if manga_data["deleted"] is True:
            #     continue

            if not (image := image_cache.get(manga_data["poster"])):
                if manga_data["poster"]:
                    image = Image(
                        **{
                            "path": manga_data["poster"],
                            "created": utcnow(),
                            "uploaded": True,
                            "ignore": False,
                            "system": True,
                        }
                    )

                    image_cache[manga_data["poster"]] = image

            start_date = utils.from_timestamp(manga_data["start_date"])
            end_date = utils.from_timestamp(manga_data["end_date"])

            manga = Manga(
                **{
                    "needs_search_update": True,
                    "year": start_date.year if start_date else None,
                    "title_original": manga_data["title_ja"],
                    "media_type": manga_data["media_type"],
                    "content_id": manga_data["content_id"],
                    "scored_by": manga_data["scored_by"],
                    "title_en": manga_data["title_en"],
                    "title_ua": manga_data["title_ua"],
                    "chapters": manga_data["chapters"],
                    "volumes": manga_data["volumes"],
                    "mal_id": manga_data["mal_id"],
                    "status": manga_data["status"],
                    "score": manga_data["score"],
                    "nsfw": manga_data["nsfw"],
                    "start_date": start_date,
                    "image_relation": image,
                    "needs_update": True,
                    "end_date": end_date,
                    "created": created,
                    "updated": updated,
                    "slug": slug,
                    "stats": {
                        "completed": 0,
                        "reading": 0,
                        "on_hold": 0,
                        "dropped": 0,
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

            add_manga.append(manga)

            # print(f"Added manga: {manga.title_original}")

    session.add_all(add_manga)
    await session.commit()
