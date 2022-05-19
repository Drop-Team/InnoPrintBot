from aiogram import types


async def privacy_command(msg: types.Message):
    """Send privacy policy"""

    text = "Our full public privacy policy - https://bit.ly/2Yu2L4z\n\n" \
           "Our privacy fundamentals:\n" \
           "• We save your Telegram account ID for identification & statistics,\n" \
           "• We permanently save file names of your document & file metadata,\n" \
           "• We temporarily (<60 minutes) save your document’s content."
    await msg.answer(text)
