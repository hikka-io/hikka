from app.sync.schedule import build_schedule, update_schedule_aired
from sqlalchemy import select
from app.models import Anime
from app import constants


async def test_schedule_aired_no_lock(
    test_session, aggregator_anime, aggregator_anime_info
):
    test_anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug
            == "shingeki-no-kyojin-the-final-season-kanketsu-hen-833be1"
        )
    )

    test_anime.status = constants.RELEASE_STATUS_ANNOUNCED
    test_anime.episodes_total = 12
    test_anime.episodes_released = None
    test_anime.schedule = [
        {"episode": 1, "airing_at": 1681354800},
        {"episode": 2, "airing_at": 1681959600},
    ]

    await build_schedule(test_session)
    await update_schedule_aired(test_session)

    assert test_anime.episodes_released == 2
    assert test_anime.status == constants.RELEASE_STATUS_ONGOING

    # Fields shouldn't be locked from MAL updates
    assert "episodes_released" not in test_anime.ignored_fields
    assert "status" not in test_anime.ignored_fields
