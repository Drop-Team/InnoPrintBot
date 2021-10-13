from datetime import datetime, timedelta, timezone
import subprocess
import shutil
import os

import PyPDF4
from PyPDF4.utils import PyPdfError

from bot.consts import FILE_LIFETIME_FOR_USER_MINUTES, FILES_PATH
import config


async def download_file(bot, doc):
    doc_id = doc.file_id

    file_name = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    file_path = FILES_PATH + file_name

    await bot.download_file_by_id(doc_id, file_path)
    return file_path


def check_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            PyPDF4.PdfFileReader(f)
        return True
    except PyPdfError:
        return False


def convert_file(file_path):
    new_file_path = file_path + ".pdf"
    if check_pdf(file_path):
        shutil.copyfile(file_path, new_file_path)
        converted = False
    else:
        subprocess.run(
            ["libreoffice", "--convert-to", "pdf", file_path, "--outdir", "/".join(new_file_path.split("/")[:-1])]
        )
        converted = True
    delete_file(file_path)
    if not os.path.isfile(new_file_path):
        return None
    return new_file_path, converted


def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        return False


class PrintingFile:
    def __init__(self, file_path):
        self.msg = None
        self.converted = None
        self.file_path = file_path

        tzinfo = timezone(timedelta(hours=3))
        self.created = datetime.now(tzinfo)

        self.pages = None
        self.set_default_pages()

        self.copies = "1"

        self.double_sided = False

        self.printed = False
        self.expired = False

    def get_pages_count(self):
        result = 0
        for part in self.pages.split(","):
            if "-" in part:
                a, b = map(int, part.split("-"))
                result += b - a + 1
            else:
                result += 1
        return result

    def set_default_pages(self):
        with open(self.file_path, "rb") as f:
            pdf_file = PyPDF4.PdfFileReader(f)
            pages_count = pdf_file.getNumPages()
        self.pages = f"1-{pages_count}" if pages_count > 1 else str(pages_count)

    def generate_caption_text(self):
        if self.printed:
            status_msg = "<i>File sent to printer.</i>"
        else:
            time = (self.created + timedelta(minutes=FILE_LIFETIME_FOR_USER_MINUTES)).strftime("%H:%M")
            status_msg = f"<i>File will be deleted in {FILE_LIFETIME_FOR_USER_MINUTES} min (at {time} MSK).</i>"

        converted_msg = ""
        if self.converted:
            converted_msg = "\n\n<i>Consider that your document has been converted into PDF format. " \
                            "It may lose some format features. Please check the preview.</i>"

        res = f"{'<b>Your document is ready to print</b>' if not self.printed else ''}" \
              f"" \
              f"{converted_msg}\n\n" \
              f"<i>Parameters (not applied on preview)</i>\n" \
              f"Pages: <b>{self.pages}</b> (total: <b>{self.get_pages_count()}</b>)\n" \
              f"Copies: <b>{self.copies}</b>\n" \
              f"Printing on both sides of the sheet: <b>{'On' if self.double_sided else 'Off'}</b>" \
              f"\n\nIf you have some problems, use /problem_print" \
              f"\n\n" + status_msg
        return res

    def print(self):
        try:
            command = ["lp", self.file_path, "-d", config.PRINTER_NAME, "-P", self.pages, "-n", self.copies]
            if not self.double_sided:
                command += ["-o", "sides=one-sided"]
            subprocess.run(command)
            self.printed = True
        except Exception as e:
            return False
        return True


def validate_pages_range(text):
    for part in text.split(","):
        nums = part.split("-")
        if len(nums) not in (1, 2):
            return False
        for num in nums:
            try:
                int(num)
            except ValueError:
                return False
    return True


def validate_copies_count(text):
    try:
        int(text)
        return True
    except ValueError:
        return False
