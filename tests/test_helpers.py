from app.auth.utils import hashpwd
from datetime import datetime
from app.models import User


async def create_user(test_session, activated=True):
    now = datetime.utcnow()

    user = User(
        **{
            "activated": activated,
            "password_hash": hashpwd("password"),
            "email": "user@mail.com",
            "username": "username",
            "last_active": now,
            "created": now,
            "login": now,
        }
    )

    test_session.add(user)
    await test_session.commit()
