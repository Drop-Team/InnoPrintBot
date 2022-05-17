from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.jobs.keyboard import JobKeyboard


class ScanJobKeyboard(JobKeyboard):
    """Scan Edit Keyboard"""

    change_multiscan_callback_data = "multiscan_change"

    def __init__(self, web_app_url: str, multiscan_enabled: bool):
        super().__init__(web_app_url)
        self.multiscan_enabled = multiscan_enabled

    def get_markup(self) -> InlineKeyboardMarkup:
        kb_markup = InlineKeyboardMarkup()
        kb_markup.row(self.get_change_multiscan_button())
        kb_markup.row(self.get_edit_properties_button())
        kb_markup.row(self.get_confirm_button(), self.get_cancel_button())
        return kb_markup

    def get_change_multiscan_button(self) -> InlineKeyboardButton:
        button_text = ("Disable" if self.multiscan_enabled else "Enable") + " MultiScan mode"
        return InlineKeyboardButton(button_text, callback_data=self.change_multiscan_callback_data)


class MultiScanKeyboard(JobKeyboard):
    """MultiScan processing keyboard"""

    stop_scanning_callback_data = "multiscan_stop"
    scan_next_callback_data = "multiscan_next"

    def get_markup(self) -> InlineKeyboardMarkup:
        kb_markup = InlineKeyboardMarkup()
        kb_markup.row(self.get_edit_properties_button())
        kb_markup.row(self.get_next_button(), self.get_stop_button())
        return kb_markup

    def get_next_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton("🟢 Scan next page(s)", callback_data=self.scan_next_callback_data)

    def get_stop_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton("🟠 Stop scanning", callback_data=self.stop_scanning_callback_data)
