from aiogram import types

from bot.utils.jobs.get_job import get_job_by_message_id


async def job_confirm(cb: types.CallbackQuery):
    """Handler for confirming job"""

    answer_message = ""
    job = get_job_by_message_id(cb.message.message_id)
    if job:
        answer_message = await job.confirm()

    await cb.answer(answer_message)


async def job_cancel(cb: types.CallbackQuery):
    """Handler for canceling job"""

    job = get_job_by_message_id(cb.message.message_id)
    if job:
        await job.cancel()

    await cb.answer()
