import os

import aiohttp

from bot.utils.logs.logger import logger
from .storage import authorized_users_ids


class User:
    """Telegram user model"""

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id

    async def is_authorized(self) -> bool:
        async with aiohttp.ClientSession() as session:
            request_url = f'{os.getenv("INNOID_API_URL")}/users/{self.telegram_id}'
            headers = {"Authorization": "Bearer " + os.getenv("INNOID_API_AUTH_TOKEN")}
            try:
                async with session.get(request_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data["is_authorized"] is True:
                            return True
            except aiohttp.client_exceptions.ClientConnectorError:
                pass

            logger.info(f"Checking is user ({self.telegram_id}) authorized from local storage")
            return self.telegram_id in authorized_users_ids
