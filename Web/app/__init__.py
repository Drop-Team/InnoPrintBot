import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import uvicorn

web_app = FastAPI()


def start():
    web_app.mount("/static", StaticFiles(directory="./app/static"), name="static")

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from .views import events, telegram

    web_app.include_router(events.router)
    web_app.include_router(telegram.router)

    uvicorn.run(
        "app:web_app",
        host="0.0.0.0", port=int(os.getenv("WEB_APP_PORT")),
        forwarded_allow_ips="*"
    )
