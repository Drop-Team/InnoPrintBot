from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from bot.utils.users.get_user import get_user


class AuthorizedFilter(BoundFilter):
    """Filter to check whether the user is authorized and allowed to use the printer"""

    key = "is_authorized"

    def __init__(self, is_authorized: bool):
        self.is_authorized = is_authorized

    async def check(self, message: types.Message):
        if self.is_authorized is None:
            return True
        return await get_user(message.from_user.id).is_authorized() == self.is_authorized
