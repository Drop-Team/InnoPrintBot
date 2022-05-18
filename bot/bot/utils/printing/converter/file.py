import os
import shutil

import PyPDF4
from PyPDF4.utils import PyPdfError
from unoserver.converter import UnoConverter


class FileNameGenerator:
    """Class for generating unique filename"""

    __counter = 0

    @classmethod
    def get_next_filename(cls) -> str:
        cls.__counter += 1
        return str(cls.__counter)


class PdfConverter:
    """Class for converting file to PDF"""
    __not_converted_file_path: str
    __converted_file_path: str
    __is_pdf: bool
    __is_converted: bool

    def __init__(self, file_path: str):
        self.__is_converted = False
        self.__not_converted_file_path = file_path
        # noinspection PyTypeChecker
        self.__converted_file_path = None
        self.__is_pdf = self.check_is_pdf()

    def check_is_pdf(self) -> bool:
        """Check if file is PDF"""
        try:
            with open(self.__not_converted_file_path, "rb") as f:
                PyPDF4.PdfFileReader(f)
            return True
        except PyPdfError:
            return False

    def convert_to_pdf(self) -> str:
        """Converts file to PDF if needed and returns new path"""
        pdf_converter = UnoConverter()

        new_path = self.__not_converted_file_path + ".pdf"

        if self.__is_pdf is True:
            shutil.copy(self.__not_converted_file_path, new_path)
            self.__converted_file_path = new_path
            return new_path

        pdf_converter.convert(inpath=self.__not_converted_file_path, outpath=new_path, convert_to="pdf")

        self.__converted_file_path = new_path
        self.__is_converted = True

        return new_path

    def is_pdf(self) -> bool:
        return self.__is_pdf

    def is_converted(self) -> bool:
        return self.__is_converted

    def close(self):
        """Remove not converted file"""

        os.remove(self.__not_converted_file_path)


def get_pdf_pages_count(file_path: str) -> int:
    try:
        with open(file_path, "rb") as f:
            pages_count = PyPDF4.PdfFileReader(f).getNumPages()
        return pages_count
    except PyPdfError:
        return 0
