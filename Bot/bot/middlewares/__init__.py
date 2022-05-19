from aiogram import Dispatcher

from .metrics import MetricsMiddleware
from .logs import LogsMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(MetricsMiddleware())
    dp.middleware.setup(LogsMiddleware())
