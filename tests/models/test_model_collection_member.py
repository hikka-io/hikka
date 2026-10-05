from sqlalchemy.exc import IntegrityError
from app import constants
import helpers
import pytest


async def test_collection_member_single_owner(
    test_session, create_test_user, create_dummy_user
):
    collection = helpers.make_collection(create_test_user)

    test_session.add_all(
        [
            collection,
            helpers.make_collection_member(
                create_test_user,
                collection=collection,
                role=constants.COLLECTION_MEMBER_OWNER,
            ),
        ]
    )

    await test_session.commit()

    # Second owner in the same collection must be rejected by the
    # partial unique index, this is what keeps ownership unambiguous
    test_session.add(
        helpers.make_collection_member(
            create_dummy_user,
            collection=collection,
            role=constants.COLLECTION_MEMBER_OWNER,
        )
    )

    with pytest.raises(IntegrityError):
        await test_session.commit()


async def test_collection_member_editor_alongside_owner(
    test_session, create_test_user, create_dummy_user
):
    collection = helpers.make_collection(create_test_user)

    test_session.add_all(
        [
            collection,
            helpers.make_collection_member(
                create_test_user,
                collection=collection,
                role=constants.COLLECTION_MEMBER_OWNER,
            ),
            helpers.make_collection_member(
                create_dummy_user,
                collection=collection,
                role=constants.COLLECTION_MEMBER_EDITOR,
            ),
        ]
    )

    # Partial index only covers owners, editors are unaffected by it
    await test_session.commit()


async def test_collection_member_owner_per_collection(
    test_session, create_test_user, create_dummy_user
):
    first = helpers.make_collection(
        create_test_user, title="First collection"
    )
    second = helpers.make_collection(
        create_dummy_user, title="Second collection"
    )

    test_session.add_all(
        [
            first,
            second,
            helpers.make_collection_member(
                create_test_user,
                collection=first,
                role=constants.COLLECTION_MEMBER_OWNER,
            ),
            helpers.make_collection_member(
                create_dummy_user,
                collection=second,
                role=constants.COLLECTION_MEMBER_OWNER,
            ),
        ]
    )

    # Index is partial per collection, not global
    await test_session.commit()


async def test_collection_member_unique_user(
    test_session, create_test_user, create_dummy_user
):
    collection = helpers.make_collection(create_test_user)

    test_session.add_all(
        [
            collection,
            helpers.make_collection_member(
                create_test_user,
                collection=collection,
                role=constants.COLLECTION_MEMBER_OWNER,
            ),
            helpers.make_collection_member(
                create_dummy_user,
                collection=collection,
                role=constants.COLLECTION_MEMBER_EDITOR,
            ),
        ]
    )

    await test_session.commit()

    # Same user must never end up with two membership rows, otherwise
    # permission checks would pick one of them at random
    test_session.add(
        helpers.make_collection_member(
            create_dummy_user,
            collection=collection,
            role=constants.COLLECTION_MEMBER_EDITOR,
            status=constants.COLLECTION_MEMBER_PENDING,
        )
    )

    with pytest.raises(IntegrityError):
        await test_session.commit()
