from app.models import User, UserOAuth, AuthToken, Client
from app.models import CollectionMember, Collection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect
from app.utils import new_token, utcnow
from datetime import timedelta
from fastapi import status
from sqlalchemy import select
from app import constants
import aiofiles
import json

from client_requests import (
    request_collection_member_invite,
    request_collection_member_accept,
    request_collection_owner_accept,
    request_collection_owner_offer,
    request_create_collection,
)


async def load_json(path):
    async with aiofiles.open(path, mode="r") as file:
        contents = await file.read()
        return json.loads(contents)


async def create_user(
    test_session,
    activated=True,
    username="testuser",
    email="user@mail.com",
    role=constants.ROLE_USER,
):
    now = utcnow()

    if not (
        user := await test_session.scalar(
            select(User).filter(User.username == username)
        )
    ):
        user = User(
            **{
                # Hash for "password"
                "password_hash": "$2b$12$ToufGsZOS/P0SfV.KzJCku/87/7q99Ls6HUZuL0/s2wiXqNJBEoRi",
                "activation_expire": utcnow() + timedelta(hours=3),
                "activation_token": new_token(),
                "email_confirmed": activated,
                "username": username,
                "last_active": now,
                "created": now,
                "email": email,
                "role": role,
                "login": now,
            }
        )

        test_session.add(user)
        await test_session.commit()

    return user


async def create_oauth(test_session, user_id):
    now = utcnow()

    oauth = UserOAuth(
        **{
            "oauth_id": "test-id",
            "provider": "google",
            "user_id": user_id,
            "last_used": now,
            "created": now,
        }
    )

    test_session.add(oauth)
    await test_session.commit()

    return oauth


async def create_token(
    test_session, email, token_secret, client: Client = None
):
    now = utcnow()

    user = await test_session.scalar(select(User).filter(User.email == email))

    token = AuthToken(
        **{
            "expiration": now + timedelta(minutes=30),
            "secret": token_secret,
            "created": now,
            "user": user,
            "client": client,
        }
    )

    test_session.add(token)
    await test_session.commit()

    return token


async def create_client(
    session: AsyncSession,
    user: User,
    secret: str,
    name: str = "TestClient",
    description: str = "Test client",
    endpoint: str = "hikka://auth/",
    verified: bool = False,
):
    now = utcnow()
    client = Client(
        **{
            "secret": secret,
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "verified": verified,
            "user": user,
            "created": now,
            "updated": now,
        }
    )

    session.add(client)
    await session.commit()

    return client


def model_to_dict(model: DeclarativeBase) -> dict:
    return {
        col.key: getattr(model, col.key)
        for col in inspect(model).mapper.column_attrs
    }


def collection_args(**kwargs):
    """Request payload for creating or updating a collection"""

    args = {
        "title": "Test collection",
        "tags": ["romance", "comedy"],
        "content_type": "anime",
        "description": "Description",
        "labels_order": ["Good"],
        "visibility": constants.COLLECTION_PUBLIC,
        "spoiler": False,
        "nsfw": False,
        "content": [
            {
                "slug": "fullmetal-alchemist-brotherhood-fc524a",
                "comment": None,
                "label": "Good",
                "order": 1,
            },
        ],
    }

    return {**args, **kwargs}


def make_collection(user, **overrides) -> Collection:
    """Unsaved collection row, for seeding without going through the API"""

    now = utcnow()

    return Collection(
        **{
            "visibility": constants.COLLECTION_PUBLIC,
            "content_type": constants.CONTENT_ANIME,
            "description": "Description",
            "title": "Test collection",
            "labels_order": [],
            "spoiler": False,
            "deleted": False,
            "vote_score": 0,
            "author": user,
            "nsfw": False,
            "entries": 0,
            "created": now,
            "updated": now,
            "tags": [],
            **overrides,
        }
    )


def make_collection_member(
    user,
    collection=None,
    collection_id=None,
    role=constants.COLLECTION_MEMBER_EDITOR,
    status=constants.COLLECTION_MEMBER_ACCEPTED,
    invited_by=None,
    created=None,
) -> CollectionMember:
    """Unsaved membership row, pass either collection or collection_id"""

    created = created or utcnow()
    target = (
        {"collection": collection}
        if collection is not None
        else {"collection_id": collection_id}
    )

    return CollectionMember(
        **{
            **target,
            "invited_by": invited_by,
            "created": created,
            "updated": created,
            "status": status,
            "user": user,
            "role": role,
        }
    )


async def create_collection_with_member(
    client,
    owner_token,
    username="dummy",
    member_token=None,
    **collection_kwargs,
):
    """
    Create a collection through the API and invite a member to it

    The invite is accepted only when member_token is given. Returns the
    collection reference.
    """

    response = await request_create_collection(
        client, owner_token, collection_args(**collection_kwargs)
    )

    assert response.status_code == status.HTTP_200_OK
    reference = response.json()["reference"]

    response = await request_collection_member_invite(
        client, reference, username, owner_token
    )

    assert response.status_code == status.HTTP_200_OK

    if member_token:
        response = await request_collection_member_accept(
            client, reference, member_token
        )

        assert response.status_code == status.HTTP_200_OK

    return reference


async def transfer_ownership(
    client, reference, username, owner_token, new_owner_token
):
    """Offer the collection to an accepted member and have them take it"""

    response = await request_collection_owner_offer(
        client, reference, username, owner_token
    )

    assert response.status_code == status.HTTP_200_OK

    response = await request_collection_owner_accept(
        client, reference, new_owner_token
    )

    assert response.status_code == status.HTTP_200_OK
