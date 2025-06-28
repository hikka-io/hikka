from app.models import Anime, Manga, Novel
from sqlalchemy import select
import helpers


async def test_anime_slug_lowercase(test_session, aggregator_anime):
    anime = await test_session.scalar(select(Anime).limit(1))
    args = helpers.model_to_dict(anime)

    await test_session.delete(anime)
    await test_session.commit()

    args["slug"] = "THIS-SLUG-IS-UPPERCASE"

    # Roundabout way of creating an Anime object in order to not break the test
    # whenever the model is changed
    anime = Anime(**args)

    test_session.add(anime)
    await test_session.commit()

    anime = await test_session.scalar(
        select(Anime).filter(Anime.slug == "this-slug-is-uppercase")
    )

    assert anime is not None


async def test_manga_slug_lowercase(test_session, aggregator_manga):
    manga = await test_session.scalar(select(Manga).limit(1))
    args = helpers.model_to_dict(manga)

    await test_session.delete(manga)
    await test_session.commit()

    args["slug"] = "THIS-SLUG-IS-UPPERCASE"

    # Roundabout way of creating a Manga object in order to not break the test
    # whenever the model is changed
    manga = Manga(**args)

    test_session.add(manga)
    await test_session.commit()

    manga = await test_session.scalar(
        select(Manga).filter(Manga.slug == "this-slug-is-uppercase")
    )

    assert manga is not None


async def test_novel_slug_lowercase(test_session, aggregator_novel):
    novel = await test_session.scalar(select(Novel).limit(1))
    args = helpers.model_to_dict(novel)

    await test_session.delete(novel)
    await test_session.commit()

    args["slug"] = "THIS-SLUG-IS-UPPERCASE"

    # Roundabout way of creating a Novel object in order to not break the test
    # whenever the model is changed
    novel = Novel(**args)

    test_session.add(novel)
    await test_session.commit()

    novel = await test_session.scalar(
        select(Novel).filter(Novel.slug == "this-slug-is-uppercase")
    )

    assert novel is not None
