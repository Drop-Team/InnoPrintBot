from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp, CommandPrivacy

from .start import start_command
from .help import help_command
from .privacy import privacy_command
from .authorization import authorize_command, is_not_authorized_error


def setup(dp: Dispatcher):
    dp.register_message_handler(start_command, CommandStart())
    dp.register_message_handler(help_command, CommandHelp())
    dp.register_message_handler(privacy_command, CommandPrivacy())
    dp.register_message_handler(authorize_command, commands="auth")
    dp.register_message_handler(is_not_authorized_error, is_authorized=False)
