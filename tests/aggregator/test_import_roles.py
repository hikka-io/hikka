from app.models import AnimeStaffRole
from sqlalchemy import select
from sqlalchemy import func


async def test_import_anime_roles(test_session, aggregator_anime_roles):
    # Make sure we imported all anime staff roles
    roles_count = await test_session.scalar(
        select(func.count(AnimeStaffRole.id))
    )

    assert roles_count == 66

    # Check individual role
    staff_role = await test_session.scalar(
        select(AnimeStaffRole).filter(AnimeStaffRole.slug == "original-creator")
    )

    assert staff_role is not None
    assert staff_role.name_en == "Original Creator"
