from .job import Job, jobs

from typing import Type


def get_job_by_id(job_id: int) -> Job:
    """Get Job by ID"""

    for job in jobs:
        if job.get_id() == job_id:
            return job


def get_job_by_message_id(message_id: int) -> Job:
    """Get Job by Telegram message ID"""

    for job in jobs:
        if job.get_message().message_id == message_id:
            return job
