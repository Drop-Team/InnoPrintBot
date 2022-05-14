import os

from aiogram import types
from aiogram.utils import exceptions

from bot.utils.printing.job.job import PrintJob
from bot.utils.printing.file import FileNameGenerator, PdfConverter
from bot.utils.metrics import metrics
# from bot.utils import PrintJob, FileNameGenerator, PdfConverter
# from bot.utils import metrics


async def print_document(msg: types.Message):
    """Handler for receiving documents and preparing it to print"""

    status_message = await msg.answer("Downloading file...")

    metrics.print_files_extensions.labels(msg.document.mime_type).inc()

    try:
        file_path = await download_file_from_message(msg)
    except exceptions.FileIsTooBig:
        await status_message.edit_text("File is too big.")
        return

    file_converter = PdfConverter(file_path)
    try:
        if not file_converter.is_pdf():
            await status_message.edit_text("Converting to PDF...")
        file_path = file_converter.convert_to_pdf()
    except Exception as e:
        await status_message.edit_text("Converting to PDF failed.")
        return
    finally:
        file_converter.close()

    job = PrintJob()
    job.set_author(msg.from_user)
    job.init_file(file_path)

    await job.send_message(msg.chat.id)
    await status_message.delete()


async def download_file_from_message(msg: types.Message) -> str:
    """Downloads file from Telegram message and returns path to file"""

    bot = msg.bot

    destination = os.getenv("FILES_PATH") + FileNameGenerator.get_next_filename()
    await bot.download_file_by_id(msg.document.file_id, destination=destination)

    return destination
