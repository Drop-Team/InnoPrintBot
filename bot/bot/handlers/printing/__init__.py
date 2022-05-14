from aiogram import Dispatcher

from .print import print_document


def setup(dp: Dispatcher):
    dp.register_message_handler(print_document, content_types=["document"], is_authorized=True)
