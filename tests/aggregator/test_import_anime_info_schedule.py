from sqlalchemy import select, func
from app.models import Anime, Edit
from app import aggregator
from app import constants
import helpers
import time


async def get_anime(test_session):
    return await test_session.scalar(
        select(Anime).filter(
            Anime.slug == "fullmetal-alchemist-brotherhood-fc524a"
        )
    )


async def get_ongoing_anime(test_session):
    anime = await get_anime(test_session)

    # Pretend schedule task has already counted few episodes
    anime.status = constants.RELEASE_STATUS_ONGOING
    anime.episodes_released = 5

    test_session.add(anime)
    await test_session.commit()

    data = await helpers.load_json("tests/data/anime_info/fma.json")
    data["status"] = constants.RELEASE_STATUS_ONGOING
    data["schedule"] = []

    return anime, data


async def count_edits(test_session):
    return await test_session.scalar(select(func.count(Edit.id)))


async def test_import_schedule_above_total(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime = await get_anime(test_session)

    # Aggregator keeps entries above episodes total (old Anilist data)
    data = await helpers.load_json("tests/data/anime_info/fma.json")
    data["schedule"] = [
        {"episode": 64, "airing_at": 1711116000},
        {"episode": 65, "airing_at": 1711720800},
    ]

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.schedule == [{"episode": 64, "airing_at": 1711116000}]

    edits_count = await count_edits(test_session)

    # Same data again shouldn't create new edits
    await aggregator.update_anime_info(test_session, anime, data)

    assert await count_edits(test_session) == edits_count


async def test_import_episodes_released_missing(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime, data = await get_ongoing_anime(test_session)

    # MAL episodes haven't been parsed yet
    data["episodes_released"] = None

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.episodes_released == 5


async def test_import_episodes_released_pending(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime, data = await get_ongoing_anime(test_session)

    # MAL counts episode by air date before it actually airs
    data["episodes_released"] = 6
    data["schedule"] = [
        {"episode": 6, "airing_at": int(time.time()) + 3600},
    ]

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.episodes_released == 5


async def test_import_episodes_released_recently_aired(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime, data = await get_ongoing_anime(test_session)

    # Episode has just aired, schedule task may not have processed it yet
    data["episodes_released"] = 6
    data["schedule"] = [
        {"episode": 6, "airing_at": int(time.time()) - 3600},
    ]

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.episodes_released == 5


async def test_import_episodes_released_not_scheduled(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime, data = await get_ongoing_anime(test_session)

    # Schedule doesn't know about episode 6 (or it aired long ago)
    data["episodes_released"] = 6
    data["schedule"] = [
        {"episode": 6, "airing_at": int(time.time()) - 3 * 86400},
    ]

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.episodes_released == 6


async def test_import_status_announced(
    test_session, aggregator_anime, aggregator_anime_info
):
    anime, data = await get_ongoing_anime(test_session)

    # Schedule marked anime as ongoing, MAL hasn't caught up yet
    data["status"] = constants.RELEASE_STATUS_ANNOUNCED

    await aggregator.update_anime_info(test_session, anime, data)

    assert anime.status == constants.RELEASE_STATUS_ONGOING
