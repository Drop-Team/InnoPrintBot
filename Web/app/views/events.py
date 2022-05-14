import os
from json.decoder import JSONDecodeError

from fastapi import Request, APIRouter, HTTPException

router = APIRouter()

events = []


@router.post("/add_event")
async def add_event(request: Request):
    """Write event's data to list"""

    try:
        data = await request.json()
    except JSONDecodeError:
        return
    events.append(data)
    print(events)


@router.get("/get_events")
async def get_events(request: Request):
    """Get all events' data as list"""

    if request.headers.get("Authorization", "") != "Bearer " + os.getenv("LONGPOLL_AUTH_TOKEN"):
        raise HTTPException(status_code=401, detail="Not authorized")

    result = {"events": events.copy()}
    events.clear()
    return result
