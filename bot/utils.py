from aiogram.types import ParseMode

import random

import config


async def send_ads(bot, user_id):
    if not config.ADVERTISEMENT:
        return
    await bot.send_message(user_id, random.choice(consts.ADS_MESSAGES),
                           parse_mode=ParseMode.HTML, disable_web_page_preview=True)
