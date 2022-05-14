import asyncio

from . import events
from . import print_jobs
from . import files_cleaner


async def main_loop(seconds: float):
    """Loop which periodically launches functions"""

    print_jobs.loops_counter.set_required_loops_number_by_seconds(seconds, 3)
    files_cleaner.loops_counter.set_required_loops_number_by_seconds(seconds, 3)

    while True:
        try:
            await events.check_for_event()

            await print_jobs.check_jobs()

            await files_cleaner.check_for_files()

        except Exception as e:
            pass
        await asyncio.sleep(seconds)
