from app.models import User


def check_consecutive(numbers: list[int]) -> bool:
    return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))


def member_log_data(user: User) -> dict:
    """Log payload naming the member a collection member action is about"""

    return {"user_id": str(user.id), "username": user.username}
