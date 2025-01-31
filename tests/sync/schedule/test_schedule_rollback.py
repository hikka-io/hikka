from app.sync.aggregator.schedule import build_schedule
from sqlalchemy import select
from app.models import Anime


async def test_schedule_rollback(
    test_session, aggregator_anime, aggregator_anime_info
):
    # First let's get anime
    test_anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug
            == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
        )
    )

    # And update number of released episodes as well as add schedule
    test_anime.episodes_released = 2
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 1681354800},
    ]

    # Now let's generate db entries for schedule
    await build_schedule(test_session)

    # Something bad happened and episode was moved to some furure date
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 9999999999},
    ]

    # Regenerate db entries for schedule again
    await build_schedule(test_session)

    # And episodes should be rolled back now
    assert test_anime.episodes_released == 1


async def test_schedule_rollback_skip(
    test_session, aggregator_anime, aggregator_anime_info
):
    # First let's get anime
    test_anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug
            == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
        )
    )

    # And update number of released episodes as well as add schedule
    test_anime.episodes_released = 2
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 1681354800},
    ]

    # Now let's generate db entries for schedule
    await build_schedule(test_session)

    # Let's say somebody just corrected release date slightly
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 1681354801},
    ]

    # Regenerate db entries for schedule again
    await build_schedule(test_session)

    # And episodes_released should be the same as before
    assert test_anime.episodes_released == 2
