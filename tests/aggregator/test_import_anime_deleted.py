from sqlalchemy import select, desc
from app.models import Anime, Log
from sqlalchemy import func
from app import aggregator
from app import constants
import helpers


async def test_import_anime_deleted(test_session, aggregator_anime):
    # TODO: this test is temporary disabled until
    # we figure out how to handle deleted titles

    # anime_count = await test_session.scalar(
    #     select(func.count(Anime.id)).filter(
    #         Anime.deleted == False,  # noqa: E712
    #     )
    # )

    # assert anime_count == 17

    # data = await helpers.load_json("tests/data/anime_deleted.json")
    # await aggregator.save_anime_list(test_session, data["list"])

    # anime_count = await test_session.scalar(
    #     select(func.count(Anime.id)).filter(
    #         Anime.deleted == False,  # noqa: E712
    #     )
    # )

    # assert anime_count == 16

    # # Check deleted anime
    # anime = await test_session.scalar(
    #     select(Anime).filter(
    #         Anime.slug == "pia-carrot-e-youkoso-sayaka-no-koi-monogatari-227414"
    #     )
    # )

    # assert anime.deleted is True

    # # Check log
    # log = await test_session.scalar(select(Log).order_by(desc(Log.created)))
    # assert log.log_type == constants.LOG_CONTENT_DELETED
    # assert log.data == {"content_type": "anime"}
    # assert log.user is None

    pass
