from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.settings import get_settings
from app.models import EmailMessage
from sqlalchemy import select
from datetime import datetime
import aiohttp

# ToDo: move website endpoint to settings
email_from = "Hikka <noreply@mail.hikka.io>"

templates = {
    "activation": {
        "subject": "Активація акаунту",
        "template": "https://hikka.io/activation/CONTENT",
    },
    "password_reset": {
        "subject": "Скидання паролю",
        "template": "https://hikka.io/reset/CONTENT",
    },
}


async def send_email(session: AsyncSession, email: EmailMessage):
    settings = get_settings()

    subject = templates[email.type]["subject"]
    template = templates[email.type]["template"].replace(
        "CONTENT", email.content
    )

    async with aiohttp.ClientSession() as aiohttp_session:
        async with aiohttp_session.post(
            settings.mailgun.endpoint,
            auth=aiohttp.BasicAuth("api", settings.mailgun.token),
            data={
                "from": email_from,
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
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        emails = await session.scalars(
            select(EmailMessage)
            .filter(EmailMessage.sent == False)  # noqa: E712
            .options(selectinload(EmailMessage.user))
            .limit(100)
        )

        for email in emails:
            await send_email(session, email)

        await session.commit()

    await sessionmanager.close()
