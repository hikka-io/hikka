from app.models import Character
from sqlalchemy import select
from sqlalchemy import func


async def test_import_characters(test_session, aggregator_characters):
    genres_count = await test_session.scalar(select(func.count(Character.id)))
    assert genres_count == 10

    # Check individual character
    character = await test_session.scalar(
        select(Character).filter(Character.slug == "lelouch-lamperouge-b1efd4")
    )

    assert character is not None
    assert character.name_en == "Lelouch Lamperouge"
    assert character.favorites == 164657
