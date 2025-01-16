from app.utils import get_settings
import aiohttp


async def send_telegram_notification(text):
    settings = get_settings()

    if not settings.aggregator.telegram_notifications:
        return

    message_thread_id = settings.aggregator.telegram_message_thread_id
    bot_token = settings.aggregator.telegram_bot_token
    chat_id = settings.aggregator.telegram_chat_id

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "message_thread_id": message_thread_id,
        "chat_id": chat_id,
        "text": text,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                print("Message sent successfully:", text)

            else:
                print("Failed to send message:", text)
