from aiogram import types
from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from bot.utils.logs.logger import logger


class LogsMiddleware(BaseMiddleware):
    """Middleware to write logs on user's actions"""

    def __init__(self):
        super(LogsMiddleware, self).__init__()

    # noinspection PyMethodMayBeStatic
    async def on_process_message(self, message: types.Message, data: dict):
        """Write logs on message"""

        handler = current_handler.get()
        handler_name = handler.__name__ if handler else "-"

        command = message.get_command()
        command_name = command if command else "-"

        author = message.from_user
        logger.info(f"{author.mention} ({author.id}) "
                    f"used command '{command_name}' "
                    f"and raised '{handler_name}' function")

    # noinspection PyMethodMayBeStatic
    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        """Write logs on callback query"""

        handler = current_handler.get()
        handler_name = handler.__name__ if handler else "-"

        callback_query_data = callback_query.data
        callback_query_data_name = callback_query_data if callback_query else "-"

        author = callback_query.from_user
        logger.info(f"{author.mention} ({author.id}) "
                    f"sent callback query '{callback_query_data_name}' "
                    f"and raised '{handler_name}' function")
