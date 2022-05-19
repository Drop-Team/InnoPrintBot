import os

import aiohttp

from bot.utils.jobs.get_job import get_job_by_id

get_events_url = os.getenv("WEB_APP_URL") + "/get_events"


async def check_for_event():
    """Check if there is Print or Scan event from Telegram Web App"""

    async with aiohttp.ClientSession() as session:
        async with session.get(
                get_events_url,
                headers={"Authorization": "Bearer {}".format(os.getenv("LONGPOLL_AUTH_TOKEN"))}
        ) as response:
            await process_response(response)


async def process_response(response: aiohttp.ClientResponse):
    """Process response from longpoll server"""

    if response.status != 200:
        return

    data = await response.json()
    events = data.get("events", None)
    if events is None:
        return

    for event in events:
        print(event)
        await process_data(event)


async def process_data(data: dict):
    """Process printing event's data"""

    job_id = data.get("job-id", None)
    if not type(job_id) is str or not job_id.isdigit():
        return

    job = get_job_by_id(int(job_id))
    if job:
        await job.set_properties(data)
