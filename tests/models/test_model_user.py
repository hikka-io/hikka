from datetime import datetime, timedelta
from sqlalchemy import select
from app.models import User


async def test_user_active(test_session, create_test_user):
    # Get test user
    user = await test_session.scalar(
        select(User).filter(User.username == "testuser")
    )

    # Make sure user active status is True
    assert user.active is True

    # Now let's travel back into past for 10 minutes
    user.last_active = datetime.utcnow() - timedelta(minutes=10)
    test_session.add(user)
    await test_session.commit()

    # User's active status now should be False
    assert user.active is False
