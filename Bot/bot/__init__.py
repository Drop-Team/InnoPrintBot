import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.utils import executor


async def on_startup(dispatcher: Dispatcher):
    from bot.utils.metrics import metrics
    from bot.utils.printing import cups_event

    bot_info = await bot.get_me()
    print(f"Logged in as {bot_info.full_name} ({bot_info.mention})")

    metrics.start_time.set_to_current_time()

    global current_event_loop
    current_event_loop = asyncio.get_event_loop()

    cups_event.subscribe()

    from bot.loops import main_loop
    current_event_loop.create_task(main_loop(0.5))

    # start_uno_server()


def start():
    from . import middlewares
    from . import filters
    from . import handlers

    middlewares.setup(dp)

    filters.setup(dp)

    handlers.info.setup(dp)
    handlers.jobs.setup(dp)
    handlers.scanning.setup(dp)
    handlers.printing.setup(dp)

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)
current_event_loop = None
