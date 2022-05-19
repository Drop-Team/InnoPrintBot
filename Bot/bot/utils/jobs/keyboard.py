from abc import ABC

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


class JobKeyboard(ABC):
    """Telegram Inline keyboard for job"""

    cancel_callback_data = "cancel_job"
    confirm_callback_data = "confirm_job"

    def __init__(self, web_app_url: str):
        self.web_app_url = web_app_url

    def get_markup(self) -> InlineKeyboardMarkup:
        kb_markup = InlineKeyboardMarkup()
        return kb_markup

    def get_edit_properties_button(self) -> InlineKeyboardButton:
        web_app = WebAppInfo(url=self.web_app_url)
        return InlineKeyboardButton("Edit parameters", web_app=web_app)

    def get_cancel_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton("❌ Cancel", callback_data=self.cancel_callback_data)

    def get_confirm_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton("✅ Confirm", callback_data=self.confirm_callback_data)
