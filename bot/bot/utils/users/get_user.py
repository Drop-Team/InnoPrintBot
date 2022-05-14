from .user import User


def get_user(telegram_id: int) -> User:
    """Get user by Telegram ID"""

    return User(telegram_id)
