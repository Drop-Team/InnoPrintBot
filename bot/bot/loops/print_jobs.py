from bot.utils.jobs.job import jobs

from .loops_counter import LoopsCounter

loops_counter = LoopsCounter()


async def check_jobs():
    """Check for expired jobs and remove jobs which are needed"""

    loops_counter.count()
    if not loops_counter.check():
        return

    for job in jobs:

        # Check for expiration
        await job.check_expired()

        # Check for removing from jobs
        if job.get_state().can_be_deleted is True:
            jobs.remove(job)
