from aiogram import types

from bot.utils.users.get_user import get_user


async def start_command(msg: types.Message):
    """Send start message"""

    if await get_user(msg.from_user.id).is_authorized():
        await msg.answer("Authorized // TODO")
    else:
        await msg.answer("Not authorized // TODO")
