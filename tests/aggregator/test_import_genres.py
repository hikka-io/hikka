from app.models import AnimeGenre
from sqlalchemy import select
from sqlalchemy import func


async def test_import_anime_genres(test_session, aggregator_anime_genres):
    # Make sure we imported all genres
    genres_count = await test_session.scalar(select(func.count(AnimeGenre.id)))
    assert genres_count == 76

    # Check whether all genres are translated
    empty_name_ua_count = await test_session.scalar(
        select(func.count(AnimeGenre.id)).filter(
            AnimeGenre.name_ua == None  # noqa: E711
        )
    )

    assert empty_name_ua_count == 0

    # Check specific genre
    genre = await test_session.scalar(
        select(AnimeGenre).filter(AnimeGenre.slug == "comedy")
    )

    assert genre is not None
    assert genre.name_en == "Comedy"
    assert genre.name_ua == "Комедія"
    assert genre.type == "genre"
