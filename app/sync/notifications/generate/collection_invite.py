from .collection_member import generate_collection_member_notification
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.models import Log
from app import constants


async def generate_collection_invite(session: AsyncSession, log: Log):
    await generate_collection_member_notification(
        session,
        log,
        constants.NOTIFICATION_COLLECTION_INVITE,
        spam_delta=timedelta(hours=6),
    )
