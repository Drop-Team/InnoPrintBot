from aiogram import types

from bot.utils.users.get_user import get_user


async def start_command(msg: types.Message):
    """Send start message"""

    text = "Welcome to @InnoPrintBot - bot for printing and scanning on the public printer " \
           "of Innopolis University on the 5th floor.\n" \
           "❓ Use /help for more info.\n\n"

    if await get_user(msg.from_user.id).is_authorized():
        text += "You are already authorized via InnoID, just send the file to print it or use the /scan command."
        await msg.answer(text)
    else:
        text += "First you have to authorize. Go to @InnoIDBot and follow its instructions."
        await msg.answer(text)
