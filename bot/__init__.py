from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from bot.command_tools.message_handlers import register_message_handlers
from bot.command_tools.callback_query import register_callback_queries
from bot.loop import main_loop
from bot import consts
import config
import asyncio

from bot.info import handlers
from bot.printing import handlers
from bot.scanning import handlers

from bot.metrics import Metrics

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


async def on_startup(dp):
    bot_info = await bot.get_me()
    print(f"Logged in as {bot_info.full_name} ({bot_info.mention})")
    Metrics.start_time.set_to_current_time()


def start():
    register_message_handlers(dp)
    register_callback_queries(dp)

    event_loop = asyncio.get_event_loop()
    event_loop.create_task(main_loop(dp))

    print("Starting bot...")
    executor.start_polling(dp, on_startup=on_startup)
