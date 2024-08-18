from sqlalchemy import delete

from app.models import AuthTokenRequest
from app import sessionmanager
from app.utils import utcnow


async def delete_expired_token_requests():
    now = utcnow()
    async with sessionmanager.session() as session:
        await session.execute(
            delete(AuthTokenRequest).filter(AuthTokenRequest.expiration < now)
        )
