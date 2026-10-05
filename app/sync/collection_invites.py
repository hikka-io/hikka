from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from app.models import CollectionMember
from sqlalchemy import delete, update
from datetime import timedelta
from app.utils import utcnow
from app import constants


async def expire_collection_invites(session: AsyncSession):
    now = utcnow()

    expired = now - timedelta(
        days=constants.COLLECTION_INVITE_EXPIRE_DAYS
    )

    # Only pending rows go, accepted members stay no matter how old.
    # Deleted outright rather than marked: the invite log is the history,
    # and a fresh invite must be possible afterwards
    await session.execute(
        delete(CollectionMember).filter(
            CollectionMember.status == constants.COLLECTION_MEMBER_PENDING,
            CollectionMember.created < expired,
        )
    )

    offer_expired = now - timedelta(
        days=constants.COLLECTION_OWNER_OFFER_EXPIRE_DAYS
    )

    # An unanswered ownership offer is only withdrawn, never deleted:
    # the row belongs to an accepted co-author, and dropping it would
    # throw them out of the collection instead of cancelling the offer
    await session.execute(
        update(CollectionMember)
        .filter(
            CollectionMember.owner_offered_at.is_not(None),
            CollectionMember.owner_offered_at < offer_expired,
        )
        .values(owner_offered_at=None)
    )

    # NOTE: sessionmanager.session() does not commit on exit, so this is
    # on us. Without it the delete is rolled back on close
    await session.commit()


async def delete_expired_collection_invites():
    async with sessionmanager.session() as session:
        await expire_collection_invites(session)
