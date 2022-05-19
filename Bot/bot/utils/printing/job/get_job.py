from bot.utils.jobs.job import Job, jobs
from .job import PrintJob


def get_job_by_cups_job_id(job_id: int) -> Job:
    """Get Job by CUPS Job ID"""

    for job in jobs:
        if type(job) is not PrintJob:
            continue
        job: PrintJob
        if job.get_cups_job_id() == job_id:
            return job
