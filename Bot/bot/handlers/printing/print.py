import os

from aiogram import types
from aiogram.utils import exceptions

from bot.utils.metrics import metrics
from bot.utils.printing.converter.file import FileNameGenerator, PdfConverter
from bot.utils.printing.job.job import PrintJob


async def print_document(msg: types.Message):
    """Handler for receiving documents and preparing it to print"""

    if msg.document is None and not msg.photo:
        text = "Please send the document you want to print (better in PDF format)."
        return await msg.answer(text)

    status_message = await msg.answer("Downloading file...")

    mime_type = msg.document.mime_type if msg.document else "[image]"
    metrics.print_files_extensions.labels(mime_type).inc()

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

    file_id: [str] = None
    if msg.document is not None:
        file_id = msg.document.file_id
    if msg.photo:
        file_id = msg.photo[-1].file_id

    await bot.download_file_by_id(file_id, destination=destination)

    return destination
