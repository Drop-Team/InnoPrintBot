import os
from typing import Optional

import cups
from aiogram import types

from bot.utils.jobs import job
from bot.utils.logs.logger import logger
from bot.utils.metrics import metrics
from . import states, properties
from .keyboard import PrintJobKeyboard
from ..cups_service.printing import print_file
from ..file import get_pdf_pages_count


class PrintJob(job.Job):
    """Job for printing"""

    _cups_job_id: int = -1
    _file_path: str

    _properties: properties.PrintProperties

    expire_in = int(os.getenv("PRINT_JOB_EXPIRED_AFTER"))
    web_app_url_postfix = "/telegram/print"
    keyboard = PrintJobKeyboard
    properties_class = properties.PrintProperties
    init_state = states.EditingState
    expired_state = states.ExpiredState

    def init_file(self, file_path: str):
        """Initialize PDF file for printing"""

        self._file_path = file_path

        pages_property = self._properties.get_property_by_type(properties.PagesProperty)
        pages_count = get_pdf_pages_count(file_path)
        pages_value = f"1-{pages_count}" if pages_count > 1 else str(pages_count)
        pages_property.set_value(pages_value)

    def get_cups_job_id(self) -> int:
        """Get CUPS Job ID"""

        return self._cups_job_id

    def get_file_path(self) -> str:
        """Get printing file path"""

        return self._file_path

    def get_message_keyboard(self) -> Optional[types.InlineKeyboardMarkup]:
        if self._state is states.EditingState:
            return PrintJobKeyboard(self.get_web_app_url()).get_markup()

    async def send_message(self, chat_id: int) -> None:
        from bot import bot

        document = types.InputFile(self._file_path, "preview.pdf")
        self._message = await bot.send_document(
            chat_id, document=document,
            caption=self.get_message_caption(),
            reply_markup=self.get_message_keyboard(),
            parse_mode=types.ParseMode.MARKDOWN
        )

    async def update_message(self):
        from bot import bot

        await bot.edit_message_caption(
            chat_id=self._message.chat.id,
            message_id=self._message.message_id,
            caption=self.get_message_caption(),
            reply_markup=self.get_message_keyboard(),
            parse_mode=types.ParseMode.MARKDOWN
        )

    async def confirm(self) -> str:
        try:
            cups_options = self._properties.get_source_properties()
            cups_options.update({"fit-to-page": "True"})
            self._cups_job_id = print_file(self._file_path, cups_options)

            await self.set_state(states.WaitingInQueueState)

            pages_total = self._properties.get_total_pages_number()
            metrics.printing.labels("jobs").inc()
            metrics.printing.labels("pages_total").inc(pages_total)

            logger.info(f"{self._author.mention} ({self._author.id}) confirmed printing "
                        f"with parameters {self._properties.get_logger_text()}")

            return ""
        except cups.IPPError as e:
            if len(e.args) >= 2:
                return e.args[1]
            return "Error sending to printer."

    async def cancel(self):
        await self.set_state(states.CancelledState)
