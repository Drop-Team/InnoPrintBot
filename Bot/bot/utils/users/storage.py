import os

import aiohttp

authorized_users_ids: list[int] = []


async def update_authorized_users():
    async with aiohttp.ClientSession() as session:
        request_url = f'{os.getenv("INNOID_API_URL")}/users'
        headers = {"Authorization": "Bearer " + os.getenv("INNOID_API_AUTH_TOKEN")}
        async with session.get(request_url, headers=headers) as resp:
            if resp.status != 200:
                return

            data = await resp.json()
            authorized_users_ids.clear()
            authorized_users_ids.extend([user["telegram_id"] for user in data["users"]])
