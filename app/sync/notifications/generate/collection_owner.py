from .collection_member import generate_collection_member_notification
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Log
from app import constants


async def generate_collection_owner(session: AsyncSession, log: Log):
    # Sent for an ownership offer, nothing is transferred yet at this point
    await generate_collection_member_notification(
        session, log, constants.NOTIFICATION_COLLECTION_OWNER
    )
