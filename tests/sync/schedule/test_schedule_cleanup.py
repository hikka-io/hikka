from app.models import Anime, AnimeSchedule
from app.sync.schedule import build_schedule
from sqlalchemy import select
from app import constants


async def get_test_anime(test_session):
    test_anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug
            == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
        )
    )

    # Schedule is only built for upcoming and ongoing anime
    test_anime.status = constants.RELEASE_STATUS_ONGOING
    test_anime.episodes_total = 12

    return test_anime


async def get_scheduled_episodes(test_session, test_anime):
    schedule = await test_session.scalars(
        select(AnimeSchedule).filter(AnimeSchedule.anime == test_anime)
    )

    return sorted(entry.episode for entry in schedule)


async def test_schedule_cleanup_upcoming(
    test_session, aggregator_anime, aggregator_anime_info
):
    test_anime = await get_test_anime(test_session)

    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 9999999999},
        {"episode": 3, "airing_at": 9999999999 + 604800},
    ]

    await build_schedule(test_session)

    assert await get_scheduled_episodes(test_session, test_anime) == [1, 2, 3]

    # Stale upcoming episode was removed from schedule by aggregator
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 9999999999},
    ]

    await build_schedule(test_session)

    # So it should be removed from our schedule as well
    assert await get_scheduled_episodes(test_session, test_anime) == [1, 2]


async def test_schedule_cleanup_keep_aired(
    test_session, aggregator_anime, aggregator_anime_info
):
    test_anime = await get_test_anime(test_session)

    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 1681959600},
    ]

    await build_schedule(test_session)

    # Aired episode is no longer in aggregator schedule
    test_anime.schedule = [
        {"episode": 2, "airing_at": 1681959600},
    ]

    await build_schedule(test_session)

    # But it has already aired, so we keep it
    assert await get_scheduled_episodes(test_session, test_anime) == [1, 2]
