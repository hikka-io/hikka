from app.models import User, AuthToken, UserOAuth, AuthTokenRequest, Client
from sqlalchemy import select, func, ScalarResult
from app.utils import hashpwd, new_token, utcnow
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import get_user_by_username
from datetime import timedelta, datetime
from starlette.datastructures import URL
from sqlalchemy.orm import selectinload
from .schemas import SignupArgs
from app import constants
import secrets
import uuid


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


async def create_oauth_user(
    session: AsyncSession, provider: str, user_data: dict[str, str]
) -> UserOAuth:
    email = user_data.get("email")
    now = utcnow()

    # I really hate this part of code
    # but we need it for better user experience
    # when new account is created via oauth
    username = secrets.token_urlsafe(16)

    # If email is present we split it and get first 32 characters
    if email:
        tmp_username = email.split("@")[0][:32]

        # Thanks @t for finding this ;)
        if len(tmp_username) > 4:
            username = tmp_username

    # Just in case
    max_attempts = 5
    attempts = 0

    while True:
        # If for some reason we exceed attempts or 64 character limit
        # Just generate random username
        if attempts > max_attempts or len(username) > 64:
            username = secrets.token_urlsafe(16)
            break

        if not (await get_user_by_username(session, username)):
            break

        username += "-" + secrets.token_urlsafe(4)
        attempts += 1

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
    # Activate user and delete token
    user.activation_expire = None
    user.activation_token = None
    user.email_confirmed = True

    # Only set user role if it's not activated
    if user.role == constants.ROLE_NOT_ACTIVATED:
        user.role = constants.ROLE_USER

    session.add(user)
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
        "redirect_url": str(
            URL(client.endpoint).replace_query_params(
                reference=request.reference
            )
        ),
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
