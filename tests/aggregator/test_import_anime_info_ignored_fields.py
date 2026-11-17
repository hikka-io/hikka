from sqlalchemy import select, func
from app.models import Anime, Edit
from app import aggregator
import helpers


async def test_import_anime_info_ignored_fields(
    test_session,
    aggregator_anime,
    aggregator_anime_info,
):
    # Check individual anime
    anime = await test_session.scalar(
        select(Anime).filter(
            Anime.slug == "fullmetal-alchemist-brotherhood-fc524a"
        )
    )

    # Change English title and add it to the ignored fields
    anime.title_en = "Changed title"
    anime.ignored_fields.append("title_en")

    # Same for the poster
    anime.ignored_fields.append("image")
    image_id = anime.image_id

    # Save changes
    test_session.add(anime)
    await test_session.commit()

    # In the meantime let's check current edit count
    edits_count = await test_session.scalar(select(func.count(Edit.id)))
    assert edits_count == 17

    # Let's try to update English title (which is in ignored fields)
    data = await helpers.load_json("tests/data/anime_info/fma.json")
    data["poster"] = (
        "/content/anime/fullmetal-alchemist-brotherhood-fc524a/new.jpg"
    )
    await aggregator.update_anime_info(test_session, anime, data)

    # It haven't been changed (right?)
    await test_session.refresh(anime)
    assert anime.title_en == "Changed title"
    assert anime.image_id == image_id

    # And since there are no changes there should be no new edits
    edits_count = await test_session.scalar(select(func.count(Edit.id)))
    assert edits_count == 17
