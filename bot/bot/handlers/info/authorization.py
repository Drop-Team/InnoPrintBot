from aiogram import types

from bot.utils.users.get_user import get_user


async def authorize_command(msg: types.Message):
    """Send information about how to authorize in the bot"""

    if await get_user(msg.from_user.id).is_authorized():
        await msg.answer("Authorized // TODO")
    else:
        await msg.answer("Not authorized // TODO")


async def is_not_authorized_error(msg: types.Message):
    """Send an error message when the user is not authorized, but is required to be"""

    await msg.answer("Have to be authorized first // TODO")
