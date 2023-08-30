from app.models import Character
from sqlalchemy import select
from sqlalchemy import func


async def test_import_characters(test_session, aggregator_characters):
    characters_count = await test_session.scalar(
        select(func.count(Character.id))
    )
    assert characters_count == 171

    # Check individual character
    character = await test_session.scalar(
        select(Character).filter(Character.slug == "edward-elric-3a3963")
    )

    assert character is not None
    assert character.name_en == "Edward Elric"
    assert character.favorites == 85959
