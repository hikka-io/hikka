from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import get_settings, utcnow
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.models import EmailMessage
from functools import lru_cache
from datetime import timedelta
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

    user_email = email.user.email

    # If user in process of changing email we send letter to new email
    if (
        email.type == constants.EMAIL_ACTIVATION
        and email.user.new_email is not None
    ):
        user_email = email.user.new_email

    async with aiohttp.ClientSession() as aiohttp_session:
        async with aiohttp_session.post(
            settings.mailgun.endpoint,
            auth=aiohttp.BasicAuth("api", settings.mailgun.token),
            data={
                "from": settings.mailgun.email_from,
                "to": [user_email],
                "subject": subject,
                "html": template,
            },
        ) as response:
            if response.status == 200:
                email.sent_time = utcnow()
                email.sent = True

                session.add(email)

                # Commit right away so email accepted by Mailgun
                # won't be sent again if something fails later on
                await session.commit()

                print(f"Sent email: {email.type}")


async def send_emails():
    """Send pending emails via Mailgun api"""

    # Tokens in our emails expire after 3 hours so there is
    # no point in retrying emails older than that
    email_lifetime = timedelta(hours=3)
    min_created = utcnow() - email_lifetime

    async with sessionmanager.session() as session:
        emails = await session.scalars(
            select(EmailMessage)
            .filter(
                EmailMessage.sent == False,  # noqa: E712
                EmailMessage.created > min_created,
            )
            .options(selectinload(EmailMessage.user))
            .order_by(EmailMessage.created.asc())
            .limit(100)
        )

        for email in emails.all():
            # One failed email shouldn't stop the rest of the batch
            try:
                await send_email(session, email)

            except Exception as e:
                print(f"Failed to send email: {email.type} ({e})")
