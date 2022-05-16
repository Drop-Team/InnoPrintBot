from aiogram import types


async def help_command(msg: types.Message):
    """Send bot commands and all useful information"""

    text = "InnoPrintBot is a bot for printing and scanning on the public printer " \
           "of Innopolis University on the 5th floor.\n" \
           "/help - Shows this message\n" \
           "/privacy - Get privacy policy\n" \
           "/auth - Get instruction for authorization\n\n" \
           "To print a file just send it a document\n" \
           "To scan, use the /scan command\n\n" \
           "Developers & Support: @DropTeamDev\n" \
           "In case of problems, write to @blinikar or @KeepError\n\n" \
           "Our products are open source, so you can find repository on GitHub: " \
           "https://github.com/blinikar/innoprintbot\n" \
           "Star if you liked it :)"

    await msg.answer(text, disable_web_page_preview=True)
