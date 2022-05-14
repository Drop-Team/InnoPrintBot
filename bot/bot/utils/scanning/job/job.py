import io
import os
from typing import Optional

from PyPDF4 import PdfFileMerger
from aiogram import types

from bot.utils.jobs import job
from bot.utils.logs.logger import logger
from bot.utils.metrics import metrics
from . import states, properties
from .keyboard import ScanJobKeyboard, MultiScanKeyboard
from ..escl.scanning import scan_document
from ..exceptions import ScanningException


class ScanJob(job.Job):
    """Job for scanning"""

    _file_path: str = None
    _multiscan_mode_enabled: bool = False
    _pdf_merger: PdfFileMerger = None

    _properties: properties.ScanProperties

    expire_in = int(os.getenv("PRINT_JOB_EXPIRED_AFTER"))
    web_app_url_postfix = "/telegram/scan"
    properties_class = properties.ScanProperties
    init_state = states.EditingState
    expired_state = states.ExpiredState

    def get_file_path(self) -> str:
        """Get scanned file path"""

        return self._file_path

    def is_multiscan_enabled(self) -> bool:
        """Returns true if multiscan mode enabled and vice versa"""

        return self._multiscan_mode_enabled

    async def change_multiscan(self):
        """Enable MultiScan mode if it disabled and vice versa, update message after this"""

        self._multiscan_mode_enabled = not self._multiscan_mode_enabled
        await self.update_message()

    def get_message_caption(self) -> str:
        text = ""
        if self._state.show_parameters:
            text += "Ready to scan. Change the parameters if necessary and confirm the scan.\n\n"

            if not self.is_multiscan_enabled():
                text += "Note that you can enable MultiScan mode. " \
                        "It will allow you to scan multiple times and get one PDF file.\n"
            text += f"• MultiScan mode is *{'on' if self.is_multiscan_enabled() else 'off'}*\n\n"

        text += super().get_message_caption()
        return text

    def get_message_keyboard(self) -> Optional[types.InlineKeyboardMarkup]:
        if self._state is states.EditingState:
            return ScanJobKeyboard(
                self.get_web_app_url(), self.is_multiscan_enabled()
            ).get_markup()
        if self._state is states.MultiScanEditingState:
            return MultiScanKeyboard(
                self.get_web_app_url()
            ).get_markup()

    async def send_message(self, chat_id: int) -> None:
        from bot import bot

        self._message = await bot.send_message(
            chat_id,
            text=self.get_message_caption(),
            reply_markup=self.get_message_keyboard(),
            parse_mode=types.ParseMode.MARKDOWN
        )

    async def update_message(self):
        from bot import bot

        await bot.edit_message_text(
            chat_id=self._message.chat.id,
            message_id=self._message.message_id,
            text=self.get_message_caption(),
            reply_markup=self.get_message_keyboard(),
            parse_mode=types.ParseMode.MARKDOWN
        )

    async def confirm(self) -> str:
        if self.is_multiscan_enabled():
            return await self.multiscan_next_document()
        else:
            return await self.scan_document()

    async def cancel(self):
        await self.set_state(states.CancelledState)

    async def scan_document(self) -> str:
        """Scan document and send it to the chat"""

        metrics.scanning.labels("default").inc()
        logger.info(f"{self._author.mention} ({self._author.id}) scanned document in default mode "
                    f"with parameters {self._properties.get_logger_text()}")

        await self.set_state(states.WaitingForDocumentState)

        try:
            pdf_document = await scan_document(self._properties.get_source_properties())
        except ScanningException as e:
            await self.set_state(states.EditingState)
            return str(e)

        await self.send_document(io.BytesIO(pdf_document))
        await self.set_state(states.CompletedState)

        return ""

    async def multiscan_next_document(self) -> str:
        """Scan next document in MultiScan mode"""

        metrics.scanning.labels("multiscan").inc()
        logger.info(f"{self._author.mention} ({self._author.id}) scanned document in multiscan mode "
                    f"with parameters {self._properties.get_logger_text()}")

        await self.set_state(states.WaitingForDocumentState)

        try:
            pdf_document = await scan_document(self._properties.get_source_properties())

            if not self._pdf_merger:
                self._pdf_merger = PdfFileMerger()

            self._pdf_merger.append(io.BytesIO(pdf_document))

        except ScanningException as e:
            return str(e)
        finally:
            await self.set_state(states.MultiScanEditingState)

    async def multiscan_stop(self) -> str:
        """Merge all scanned documents in MultiScan mode and send merged document to the chat"""

        with io.BytesIO() as document:
            self._pdf_merger.write(document)
            self._pdf_merger.close()
            document.seek(0)

            await self.send_document(document)

        await self.set_state(states.CompletedState)
        return ""

    async def send_document(self, pdf_document: io.IOBase):
        """Send document to the chat"""

        doc = types.InputFile(pdf_document, "document.pdf")
        await self._message.answer_document(
            document=doc,
            caption="Here is scanned document"
        )
