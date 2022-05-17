from bot.utils.jobs.job import jobs

from .metrics import active_jobs_count


def active_jobs_count_update():
    active_jobs_count.set(int(len(jobs)))
