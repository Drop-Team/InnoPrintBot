import asyncio

from bot import consts
from bot import metrics
from bot.printing.handlers import check_printing_files
from bot.scanning.handlers import check_scanning_jobs


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

        await metrics.is_connected_to_printer_update()

        await asyncio.sleep(consts.MAIN_LOOP_DELAY)
