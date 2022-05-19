from aiogram import types

from bot.utils.jobs.get_job import get_job_by_message_id
from bot.utils.scanning.job.job import ScanJob


async def multiscan_change(cb: types.CallbackQuery):
    """Handler for receiving documents and preparing it to print"""

    # noinspection PyTypeChecker
    job = get_job_by_message_id(cb.message.message_id)
    if job and type(job) is ScanJob:
        job: ScanJob
        await job.change_multiscan()

    await cb.answer()


async def multiscan_stop(cb: types.CallbackQuery):
    """Handler for receiving documents and preparing it to print"""

    # noinspection PyTypeChecker
    job = get_job_by_message_id(cb.message.message_id)
    if job and type(job) is ScanJob:
        job: ScanJob
        await job.multiscan_stop()

    await cb.answer()


async def multiscan_next(cb: types.CallbackQuery):
    """Handler for receiving documents and preparing it to print"""

    # noinspection PyTypeChecker
    job = get_job_by_message_id(cb.message.message_id)
    if job and type(job) is ScanJob:
        job: ScanJob
        await job.multiscan_next_document()

    await cb.answer()
