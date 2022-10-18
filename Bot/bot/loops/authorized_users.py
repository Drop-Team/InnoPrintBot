from bot.utils.users.storage import update_authorized_users
from .loops_counter import LoopsCounter

loops_counter = LoopsCounter()


async def update_users():
    """Update authorized users storage"""

    loops_counter.count()
    if not loops_counter.check():
        return

    await update_authorized_users()
