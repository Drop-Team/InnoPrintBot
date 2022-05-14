from aiogram import types
from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from bot.utils.metrics import metrics


class MetricsMiddleware(BaseMiddleware):
    """Middleware to write Prometheus metrics on user's actions"""

    def __init__(self):
        super(MetricsMiddleware, self).__init__()

    # noinspection PyMethodMayBeStatic
    async def on_process_message(self, message: types.Message, data: dict):
        """Write Message metric"""

        handler = current_handler.get()
        handler_name = handler.__name__ if handler else "-"

        command = message.get_command()
        command_name = command if command else "-"

        metrics.message_handlers.labels(handler_name, command_name).inc()

    # noinspection PyMethodMayBeStatic
    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        """Write Callback query metric"""

        handler = current_handler.get()
        handler_name = handler.__name__ if handler else "-"

        callback_query_data = callback_query.data
        callback_query_data_name = callback_query_data if callback_query else "-"

        metrics.callback_query_handlers.labels(handler_name, callback_query_data_name).inc()
