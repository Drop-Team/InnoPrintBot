import os

from . import cups_connection


def print_file(filename: str, options: dict) -> int:
    """Sends file to printer with specified print options and returns Job ID"""

    return cups_connection.printFile(
        os.getenv("CUPS_PRINTER_NAME"), filename=filename, title="InnoPrintBot Job", options=options
    )
