from aiogram.types import InlineKeyboardMarkup

from bot.utils.jobs.keyboard import JobKeyboard


class PrintJobKeyboard(JobKeyboard):
    """Print Keyboard"""

    def get_markup(self) -> InlineKeyboardMarkup:
        kb_markup = InlineKeyboardMarkup()
        kb_markup.row(self.get_edit_properties_button())
        kb_markup.row(self.get_confirm_button(), self.get_cancel_button())
        return kb_markup
