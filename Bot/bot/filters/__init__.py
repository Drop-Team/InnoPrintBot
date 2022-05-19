from aiogram import Dispatcher

from .is_authorized import AuthorizedFilter


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AuthorizedFilter)
