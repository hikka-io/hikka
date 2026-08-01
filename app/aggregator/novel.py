from app.models import Novel, Image
from sqlalchemy import select
from app.utils import utcnow
from app import utils


async def save_novel_list(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["poster"] for entry in data]

    cache = await session.scalars(
        select(Novel).filter(Novel.content_id.in_(content_ids))
    )

    novel_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).filter(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_novel = []

    for novel_data in data:
        slug = utils.slugify(novel_data["title_ja"], novel_data["content_id"])
        created = utils.from_timestamp(novel_data["created"])
        updated = utils.from_timestamp(novel_data["updated"])

        if novel_data["content_id"] in novel_cache:
            novel = novel_cache[novel_data["content_id"]]

            # TODO: this is temporary solution, eventually we shoud fix that
            # if novel.deleted is False and novel_data["deleted"] is True:
            #     novel.needs_search_update = True
            #     novel.deleted = True
            #     session.add(novel)

            #     await service.create_log(
            #         session,
            #         constants.LOG_CONTENT_DELETED,
            #         None,
            #         novel.id,
            #         {
            #             "content_type": constants.CONTENT_NOVEL,
            #         },
            #     )

            #     continue

            if novel.created is None:
                novel.created = created

            if updated == novel.aggregator_updated:
                continue

            if novel.needs_update:
                continue

            novel.needs_update = True

            # print(f"Novel needs update: {novel.title_original}")

        else:
            # if novel_data["deleted"] is True:
            #     continue

            if not (image := image_cache.get(novel_data["poster"])):
                if novel_data["poster"]:
                    image = Image(
                        **{
                            "path": novel_data["poster"],
                            "created": utcnow(),
                            "uploaded": True,
                            "ignore": False,
                            "system": True,
                        }
                    )

                    image_cache[novel_data["poster"]] = image

            start_date = utils.from_timestamp(novel_data["start_date"])
            end_date = utils.from_timestamp(novel_data["end_date"])

            novel = Novel(
                **{
                    "needs_search_update": True,
                    "year": start_date.year if start_date else None,
                    "title_original": novel_data["title_ja"],
                    "media_type": novel_data["media_type"],
                    "content_id": novel_data["content_id"],
                    "scored_by": novel_data["scored_by"],
                    "title_en": novel_data["title_en"],
                    "title_ua": novel_data["title_ua"],
                    "chapters": novel_data["chapters"],
                    "volumes": novel_data["volumes"],
                    "mal_id": novel_data["mal_id"],
                    "status": novel_data["status"],
                    "score": novel_data["score"],
                    "nsfw": novel_data["nsfw"],
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

            add_novel.append(novel)

            # print(f"Added novel: {novel.title_original}")

    session.add_all(add_novel)
    await session.commit()
