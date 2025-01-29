from app.utils import get_settings
from datetime import timedelta
import aiohttp
import time


def pluralize_ukrainian(value, singular, plural_gen, plural_acc):
    if 11 <= value % 100 <= 14:
        return plural_acc
    elif value % 10 == 1:
        return singular
    elif 2 <= value % 10 <= 4:
        return plural_gen
    else:
        return plural_acc


def format_timedelta_uk(tdelta):
    days = tdelta.days
    seconds = tdelta.seconds
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days > 0:
        label = pluralize_ukrainian(days, "день", "дні", "днів")
        parts.append(f"{days} {label}")
    if hours > 0:
        label = pluralize_ukrainian(hours, "годину", "години", "годин")
        parts.append(f"{hours} {label}")
    if minutes > 0:
        label = pluralize_ukrainian(minutes, "хвилину", "хвилини", "хвилин")
        parts.append(f"{minutes} {label}")
    if seconds > 0 or not parts:
        label = pluralize_ukrainian(seconds, "секунду", "секунди", "секунд")
        parts.append(f"{seconds} {label}")

    return " ".join(parts)


class SyncTracker:
    def __init__(self):
        self.completed_tasks = []
        self.current_task_start = None
        self.current_task = None
        self.start_time = time.time()

    def add_task(self, task_name: str):
        if self.current_task is not None:
            duration = round(time.time() - self.current_task_start)
            self.completed_tasks.append((self.current_task, duration))

        self.current_task = task_name
        self.current_task_start = time.time()

    def get_status_message(self) -> str:
        lines = ["Починаю синхронізацію з агрегатором..."]

        if bool(self.completed_tasks or self.current_task):
            lines.append("")

        for completed_task, duration in self.completed_tasks:
            time_spent = format_timedelta_uk(timedelta(seconds=duration))
            lines.append(f"{completed_task[1]} за {time_spent}")

        if self.current_task:
            if len(self.completed_tasks) > 0:
                lines.append("")

            lines.append(f"{self.current_task[0]}...")

        return "\n".join(lines)

    def get_final_message(self) -> str:
        if self.current_task is not None:
            duration = round(time.time() - self.current_task_start)
            self.completed_tasks.append((self.current_task, duration))
            self.current_task = None
            self.current_task_start = None

        message = self.get_status_message()

        total_duration = round(time.time() - self.start_time)
        total_time_spent = format_timedelta_uk(
            timedelta(seconds=total_duration)
        )

        message += f"\n\nГотово, синхронізація зайняла {total_time_spent}!"
        return message


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
            response_data = await response.json()

            if response.status != 200:
                print("Failed to send message:", response_data)
                return None

            else:
                return response_data["result"]["message_id"]


async def update_telegram_message(message_id, new_text):
    settings = get_settings()

    if message_id is None:
        return

    if not settings.aggregator.telegram_notifications:
        return

    bot_token = settings.aggregator.telegram_bot_token
    chat_id = settings.aggregator.telegram_chat_id

    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status != 200:
                response_data = await response.json()
                print("Failed to update message:", response_data)
