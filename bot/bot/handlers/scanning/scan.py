import os

from aiogram import types
from aiogram.utils import exceptions

from bot.utils.scanning.job.job import ScanJob
from bot.utils.metrics import metrics


async def scan_document(msg: types.Message):
    """Handler for receiving documents and preparing it to print"""

    job = ScanJob()
    job.set_author(msg.from_user)

    await job.send_message(msg.chat.id)
