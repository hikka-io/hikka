from service.models import EmailMessage
from tortoise import Tortoise
from datetime import datetime
import aiohttp
import config

# This task responsible for sending emails via Mailgun api
async def send_emails():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    emails = await EmailMessage.filter(
        sent=False
    ).prefetch_related("receiver").limit(100)

    for email in emails:
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
                    "to": [email.receiver.email],
                    "subject": subject,
                    "text": template
                }) as response:
                    if response.status != 200:
                        print(f"Failed send email to {email.receiver.email}")
                        continue

                    email.sent_time = datetime.utcnow()
                    email.sent = True
                    await email.save()

                    print(f"Sent email: {email.type}")
