from aiogram import types


async def privacy_command(msg: types.Message):
    """Send privacy policy"""

    text = "// TODO"
    await msg.answer(text)
