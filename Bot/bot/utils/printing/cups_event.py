import asyncio
import os
import re
from typing import NamedTuple, Type, Optional

from cups_notify import event

from bot.utils.logs.logger import logger
from .cups_service import cups_subscription
from .job import states
from .job.get_job import get_job_by_cups_job_id
from .job.states import JobState


class StateRegex(NamedTuple):
    regex: str
    state: Type[JobState]


states_regex = [
    StateRegex(regex=r".*canceled.*", state=states.CancelledState),
    StateRegex(regex=r"Connecting to printer.", state=states.ConnectingToPrinterState),
    StateRegex(regex=r"The printer is not responding.", state=states.PrinterNotRespondingState),
    StateRegex(regex=r"Waiting for job to complete.", state=states.PrintingDocumentState),
    StateRegex(regex=r"Job completed.*", state=states.CompletedState)
]


def subscribe():
    """Add subscription to CUPS events"""

    from bot import current_event_loop
    sub = cups_subscription

    sub.subscribe(lambda evt: asyncio.run_coroutine_threadsafe(on_event(evt), current_event_loop),
                  [event.CUPS_EVT_JOB_CREATED,
                   event.CUPS_EVT_JOB_COMPLETED,
                   event.CUPS_EVT_JOB_PROGRESS,
                   event.CUPS_EVT_JOB_STOPPED])


async def on_event(cups_event: event.CupsEvent):
    """CUPS event handler"""

    logger.info("CUPS Event: " + cups_event.title)

    title = cups_event.title
    description = cups_event.description

    cups_job_id = get_job_id(title)
    if cups_job_id is None:
        return

    job = get_job_by_cups_job_id(cups_job_id)
    if job is None:
        return

    new_job_state = get_job_state(description)
    if new_job_state is None:
        return

    await job.set_state(new_job_state)


def get_job_id(title: str) -> Optional[int]:
    """Parsing job ID from CUPS event title"""

    printer_name = os.getenv("CUPS_PRINTER_NAME")

    pattern = rf"Print Job: {printer_name}-(\d+) .+"
    match = re.fullmatch(pattern, title)
    if match is None:
        return

    job_id = int(match.group(1))

    return job_id


def get_job_state(description: str) -> Type[states.JobState]:
    """Get JobState by checking description for regex match"""

    for state_regex in states_regex:
        if re.fullmatch(state_regex.regex, description):
            return state_regex.state
