from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.models import EmailMessage
from sqlalchemy import select
from datetime import datetime
import aiohttp
import config


async def send_email(session: AsyncSession, email: EmailMessage):
    subject = config.email["templates"][email.type]["subject"]
    template = config.email["templates"][email.type]["template"].replace(
        "CONTENT", email.content
    )

    async with aiohttp.ClientSession() as aiohttp_session:
        async with aiohttp_session.post(
            config.mailgun["endpoint"],
            auth=aiohttp.BasicAuth("api", config.mailgun["token"]),
            data={
                "from": config.email["from"],
                "to": [email.user.email],
                "subject": subject,
                "text": template,
            },
        ) as response:
            if response.status == 200:
                email.sent_time = datetime.utcnow()
                email.sent = True

                session.add(email)

                print(f"Sent email: {email.type}")


# This task responsible for sending emails via Mailgun api
async def send_emails():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        emails = await session.scalars(
            select(EmailMessage)
            .filter_by(sent=False)
            .options(selectinload(EmailMessage.user))
            .limit(100)
        )

        for email in emails:
            await send_email(session, email)

        await session.commit()
