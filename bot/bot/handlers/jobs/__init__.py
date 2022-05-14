from aiogram import Dispatcher

from .buttons import job_confirm, job_cancel


def setup(dp: Dispatcher):
    dp.register_callback_query_handler(job_confirm, text="confirm_job", is_authorized=True)
    dp.register_callback_query_handler(job_cancel, text="cancel_job", is_authorized=True)
