from aiogram import types


async def help_command(msg: types.Message):
    """Send bot commands and all useful information"""

    text = "// TODO"
    await msg.answer(text)
