from aiogram import types

from bot.utils.users.get_user import get_user


async def authorize_command(msg: types.Message):
    """Send information about how to authorize in the bot"""

    if await get_user(msg.from_user.id).is_authorized():
        await msg.answer("You are already authorized. Use /help to get commands.")
    else:
        await msg.answer("To access the printer, go to @InnoIDBot and follow its instructions.")


async def is_not_authorized_error(msg: types.Message):
    """Send an error message when the user is not authorized, but is required to be"""

    text = "First you have to confirm that you are a student or an employee of Innopolis University.\n" \
           "Use /auth command."
    await msg.answer(text)
