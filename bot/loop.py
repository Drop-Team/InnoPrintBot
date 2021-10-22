import asyncio

from bot.printing.handlers import check_printing_files
from bot.scanning.handlers import check_scanning_jobs
from bot import consts


async def main_loop(dp):
    while True:
        try:
            await check_printing_files(dp)
        except Exception as e:
            pass

        try:
            await check_scanning_jobs(dp)
        except Exception as e:
            pass

        await asyncio.sleep(consts.MAIN_LOOP_DELAY)
