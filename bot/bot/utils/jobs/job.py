import os
from abc import ABC
from datetime import datetime, timedelta
from typing import List, Optional, Type

from aiogram import types

from . import states
from .properties import Properties

from bot.utils.ads.generator import get_ad


class Job(ABC):
    """Job with opportunity to change properties and confirm"""

    _id: int
    _state: Type[states.JobState]
    _created: datetime

    _message: types.Message
    _author: types.User

    _properties: Properties

    expire_in = 0  # in minutes
    web_app_url_postfix = "/telegram/..."
    properties_class: Type[Properties] = Properties
    init_state: Type[states.JobState]
    expired_state: Type[states.JobState]

    def __init__(self):
        self._id = job_counter.get_next()
        jobs.append(self)
        self._created = datetime.now()
        self._properties = self.properties_class()
        self._state = self.init_state

    def get_id(self) -> int:
        """Get Job ID"""
        return self._id

    def get_message(self) -> types.Message:
        """Get job's Telegram message"""
        return self._message

    async def set_state(self, state: Type[states.JobState]) -> None:
        """Rewrite state and update job's message"""
        self._state = state
        await self.update_message()

    def get_state(self) -> Type[states.JobState]:
        """Get current state"""
        return self._state

    def set_author(self, job_author: types.User):
        """Set job author as Telegram User"""
        self._author = job_author

    def get_message_caption(self) -> str:
        """Get caption for telegram message"""

        text = ""

        if self._state.show_parameters is True:
            text += self._properties.get_readable_text() + "\n\n"

        if self._state.text is not None:
            text += self._state.text + "\n\n"

        if self._state.show_expired_in is True:
            expire_in = self.expire_in
            time = (self._created + timedelta(minutes=expire_in)).strftime("%H:%M")
            text += f"Job will be expired in {expire_in} min (at {time} MSK)" + "\n\n"

        if self._state.show_ad is True:
            text += get_ad() + "\n\n"

        return text

    # noinspection PyMethodMayBeStatic
    def get_message_keyboard(self) -> Optional[types.InlineKeyboardMarkup]:
        """Get keyboard for telegram message"""

        return None

    def get_web_app_url(self) -> str:
        """Get URL for Telegram Web App"""

        web_app_base_url = os.getenv("WEB_APP_URL") + self.web_app_url_postfix
        url_params = self._properties.get_webapp_url_params(str(self._id))
        web_app_url = f"{web_app_base_url}?{url_params}"
        return web_app_url

    async def set_properties(self, properties: dict):
        self._properties.update_webapp_values(properties)
        await self.update_message()

    async def check_expired(self) -> None:
        """Check if job is expired (expiration date specified in .env in minutes) and makes it expired if needed"""

        difference = (datetime.now() - self._created).seconds
        if difference > self.expire_in * 60:
            await self.set_state(self.expired_state)

    async def send_message(self, chat_id: int):
        """Send message with properties and remember it for future editing"""

        # Do something

    async def update_message(self):
        """Update message with properties"""

        # Do something

    async def confirm(self) -> str:
        """Confirm job (calls when user press confirm button on message)"""

        # Do something

    async def cancel(self):
        """Cancel job (calls when user press cancel button on message)"""

        # Do something


class JobCounter:
    """Counter for generating unique Job ID"""

    def __init__(self):
        self.count = 0

    def get_next(self):
        self.count += 1
        return self.count


jobs: List[Job] = list()
job_counter = JobCounter()
