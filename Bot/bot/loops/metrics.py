from bot.utils.metrics.jobs import active_jobs_count_update
from bot.utils.metrics.printer_availability import is_printer_available_update
from .loops_counter import LoopsCounter

loops_counter = LoopsCounter()


async def update_metrics():
    """Update prometheus metrics"""

    loops_counter.count()
    if not loops_counter.check():
        return

    is_printer_available_update()
    active_jobs_count_update()
