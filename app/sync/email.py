from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_settings, utcnow
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.models import EmailMessage
from functools import lru_cache
from sqlalchemy import select
from app import constants
import aiohttp


subjects = {
    constants.EMAIL_PASSWORD_RESET: "Скидання паролю",
    constants.EMAIL_ACTIVATION: "Підтвердження пошти",
}


@lru_cache()
def read_file(path: str):
    with open(path, mode="r") as file:
        return file.read()


# NOTE: I really hate hardcoded paths here
# Is there another way to do that (?)
async def get_template(email_type: str):
    if email_type == constants.EMAIL_ACTIVATION:
        return read_file("app/sync/data/confirm-email.markup")

    if email_type == constants.EMAIL_PASSWORD_RESET:
        return read_file("app/sync/data/password-reset.markup")

    return None


async def send_email(session: AsyncSession, email: EmailMessage):
    settings = get_settings()

    # In case something terrible happens to our templates
    if not (template := await get_template(email.type)):
        return

    # Replace token and username in template
    # NOTE: This code would work only if template has username and token
    # We need better way to handle that
    template = template.replace("{username}", email.user.username)
    template = template.replace("{token}", email.content)
    subject = subjects[email.type]

    async with aiohttp.ClientSession() as aiohttp_session:
        async with aiohttp_session.post(
            settings.mailgun.endpoint,
            auth=aiohttp.BasicAuth("api", settings.mailgun.token),
            data={
                "from": settings.mailgun.email_from,
                "to": [email.user.email],
                "subject": subject,
                "html": template,
            },
        ) as response:
            if response.status == 200:
                email.sent_time = utcnow()
                email.sent = True

                session.add(email)

                print(f"Sent email: {email.type}")


async def send_emails():
    """Send pending emails via Mailgun api"""

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
