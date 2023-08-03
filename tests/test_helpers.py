from app.auth.utils import hashpwd, new_token
from datetime import datetime, timedelta
from app.models import User


async def create_user(test_session, activated=True):
    now = datetime.utcnow()

    user = User(
        **{
            "activation_expire": datetime.utcnow() + timedelta(hours=3),
            "password_hash": hashpwd("password"),
            "activation_token": new_token(),
            "email": "user@mail.com",
            "activated": activated,
            "username": "username",
            "last_active": now,
            "created": now,
            "login": now,
        }
    )

    test_session.add(user)
    await test_session.commit()
