from aiogram import Dispatcher

from .scan import scan_document
from .buttons import multiscan_change, multiscan_stop, multiscan_next


def setup(dp: Dispatcher):
    dp.register_message_handler(scan_document, commands=["scan"], is_authorized=True)
    dp.register_callback_query_handler(multiscan_change, text="multiscan_change", is_authorized=True)
    dp.register_callback_query_handler(multiscan_stop, text="multiscan_stop", is_authorized=True)
    dp.register_callback_query_handler(multiscan_next, text="multiscan_next", is_authorized=True)
