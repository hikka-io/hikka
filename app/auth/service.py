from app.models import User, AuthToken, UserOAuth, AuthTokenRequest, Client
from sqlalchemy import select, func, ScalarResult
from app.utils import hashpwd, new_token, utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from app.service import get_user_by_email
from datetime import timedelta, datetime
from starlette.datastructures import URL
from sqlalchemy.orm import selectinload
from app.utils import is_valid_username
from .schemas import SignupArgs
from urllib.parse import quote
from app import constants
import secrets
import uuid
import re


async def get_user_by_activation(
    session: AsyncSession, token: str
) -> User | None:
    return await session.scalar(
        select(User).filter(User.activation_token == token)
    )


async def get_oauth_by_id(
    session: AsyncSession, oauth_id: str, provider: str
) -> UserOAuth | None:
    return await session.scalar(
        select(UserOAuth)
        .filter(
            UserOAuth.provider == provider,
            UserOAuth.oauth_id == oauth_id,
        )
        .options(selectinload(UserOAuth.user))
    )


async def get_user_by_reset(session: AsyncSession, token: str) -> User | None:
    return await session.scalar(
        select(User).filter(User.password_reset_token == token)
    )


def username_from_email(email: str | None) -> str | None:
    """Make username from email or return None if it can't be valid"""

    if not email:
        return None

    # Characters usernames can't have become underscores
    # and leading ones are dropped since username can't start with one
    username = re.sub(r"[^A-Za-z0-9_]", "_", email.split("@")[0])
    username = username.lstrip("_")[:32]

    # All digit names like phone numbers fail since letter is required
    return username if is_valid_username(username) else None


async def generate_oauth_username(
    session: AsyncSession, email: str | None
) -> str:
    """Pick free username for new oauth account"""

    # Name from email goes first and then same name with random suffix
    if username := username_from_email(email):
        candidates = [username] + [
            f"{username}_{secrets.token_hex(3)}" for _ in range(5)
        ]

        for candidate in candidates:
            if not await get_user_by_username(session, candidate):
                return candidate

    # Random username always matches username rules
    while True:
        username = f"user_{secrets.token_hex(6)}"

        if not await get_user_by_username(session, username):
            return username


async def create_oauth_user(
    session: AsyncSession, provider: str, user_data: dict[str, str]
) -> UserOAuth:
    email = user_data.get("email")
    username = await generate_oauth_username(session, email)
    now = utcnow()

    user = User(
        **{
            "needs_search_update": True,
            "email_confirmed": email is not None,
            "role": constants.ROLE_USER,
            "password_hash": None,
            "username": username,
            "last_active": now,
            "email": email,
            "created": now,
            "login": now,
        }
    )

    oauth = UserOAuth(
        **{
            "oauth_id": user_data["id"],
            "provider": provider,
            "last_used": now,
            "created": now,
            "user": user,
        }
    )

    session.add(user)
    session.add(oauth)
    await session.commit()

    return oauth


async def update_oauth_timestamp(session: AsyncSession, oauth: UserOAuth):
    now = utcnow()
    oauth.last_used = now

    session.add(oauth)
    await session.commit()


async def create_user(session: AsyncSession, signup: SignupArgs) -> User:
    password_hash = hashpwd(signup.password)
    activation_token = new_token()
    now = utcnow()

    user = User(
        **{
            "needs_search_update": True,
            "role": constants.ROLE_NOT_ACTIVATED,
            "activation_expire": now + timedelta(hours=3),
            "activation_token": activation_token,
            "password_hash": password_hash,
            "username": signup.username,
            "email": signup.email,
            "last_active": now,
            "created": now,
            "login": now,
        }
    )

    session.add(user)
    await session.commit()

    return user


async def create_auth_token(session: AsyncSession, user: User) -> AuthToken:
    now = utcnow()

    # Update user login time
    user.login = now

    # After auth token will be valid only for 30 minutes
    # If unused it will expire
    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": new_token(),
            "created": now,
            "used": now,
            "user": user,
        }
    )

    session.add_all([user, token])
    await session.commit()

    return token


async def create_password_token(session: AsyncSession, user: User) -> User:
    # Generate new password reset token
    user.password_reset_expire = utcnow() + timedelta(hours=3)
    user.password_reset_token = new_token()

    session.add(user)
    await session.commit()

    return user


async def activate_user(session: AsyncSession, user: User) -> User:
    success = True

    # Special case for email change
    if user.new_email is not None:
        if not await get_user_by_email(session, user.new_email):
            user.email = user.new_email
            user.new_email = None

        else:
            success = False

    # Activate user and delete token
    user.activation_expire = None
    user.activation_token = None

    if success:
        user.email_confirmed = True

        # Only set user role if it's not activated
        if user.role == constants.ROLE_NOT_ACTIVATED:
            user.role = constants.ROLE_USER

    await session.commit()

    return user


async def change_password(session: AsyncSession, user: User, new_password: str):
    # Set new password and delete reset token
    user.password_hash = hashpwd(new_password)
    user.password_reset_expire = None
    user.password_reset_token = None

    session.add(user)
    await session.commit()

    return user


def build_redirect_url(endpoint: str, reference: str) -> str:
    if "{reference}" in endpoint:
        return endpoint.replace("{reference}", quote(reference, safe=""))

    return str(URL(endpoint).replace_query_params(reference=reference))


async def create_auth_token_request(
    session: AsyncSession, user: User, client: Client, scope: list[str]
) -> dict:
    # Remove duplicates in scope (just in case)
    scope = list(set(scope))

    now = utcnow()

    request = AuthTokenRequest(
        **{
            "expiration": now + timedelta(minutes=1),
            "created": now,
            "user": user,
            "client": client,
            "scope": scope,
        }
    )
    session.add(request)
    await session.commit()

    return {
        "reference": request.reference,
        "expiration": request.expiration,
        "redirect_url": build_redirect_url(client.endpoint, request.reference),
    }


async def get_auth_token_request(
    session: AsyncSession, reference: str | uuid.UUID
) -> AuthTokenRequest:
    return await session.scalar(
        select(AuthTokenRequest)
        .filter(AuthTokenRequest.id == reference)
        .options(
            selectinload(AuthTokenRequest.user),
            selectinload(AuthTokenRequest.client),
        )
    )


async def create_auth_token_from_request(
    session: AsyncSession, request: AuthTokenRequest
):
    token = await create_auth_token(session, request.user)

    # Add client and scope to just created token
    token.client = request.client
    token.scope = request.scope

    # Expire token request
    request.expiration = utcnow() - timedelta(minutes=1)

    await session.commit()

    return token


async def count_user_thirdparty_auth_tokens(
    session: AsyncSession, user: User, now: datetime
) -> int:
    return await session.scalar(
        select(func.count(AuthToken.id)).filter(
            AuthToken.user_id == user.id,
            AuthToken.client_id.is_not(None),
            AuthToken.expiration >= now,
        )
    )


async def list_user_thirdparty_auth_tokens(
    session: AsyncSession,
    user: User,
    offset: int,
    limit: int,
    now: datetime,
) -> ScalarResult[AuthToken]:
    return await session.scalars(
        select(AuthToken)
        .options(selectinload(AuthToken.client).selectinload(Client.user))
        .filter(
            AuthToken.user_id == user.id,
            AuthToken.client_id.is_not(None),
            AuthToken.expiration >= now,
        )
        .offset(offset)
        .limit(limit)
    )


async def get_auth_token(
    session: AsyncSession, reference: str | uuid.UUID
) -> AuthToken:
    return await session.scalar(
        select(AuthToken)
        .filter(AuthToken.id == reference)
        .options(
            selectinload(AuthToken.client).selectinload(Client.user),
            selectinload(AuthToken.user),
        )
    )


async def revoke_auth_token(session: AsyncSession, token: AuthToken):
    await session.delete(token)
    await session.commit()

    return token
