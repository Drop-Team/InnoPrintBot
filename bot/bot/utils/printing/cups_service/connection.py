import os

import cups


def create_connection() -> cups.Connection:
    """Create connection with CUPS server, setup printer and create subscription"""

    # Create connection
    setup_cups()
    conn = cups.Connection()

    # Setup printer
    create_printer(conn)

    return conn


def setup_cups():
    """Configure CUPS"""
    cups.setServer(os.getenv("CUPS_SERVER"))
    cups.setPort(int(os.getenv("CUPS_PORT")))
    cups.setUser(os.getenv("CUPS_USER"))
    cups.setPasswordCB(lambda t: os.getenv("CUPS_PASSWORD"))


def create_printer(connection: cups.Connection):
    """Create and configure CUPS printer"""

    printer_uri = f"{os.getenv('CUPS_PRINTER_PROTOCOL')}://" \
                  f"{os.getenv('PRINTER_HOST')}:{os.getenv('CUPS_PRINTER_PORT')}"

    connection.deletePrinter(os.getenv("CUPS_PRINTER_NAME"))
    connection.addPrinter(
        os.getenv("CUPS_PRINTER_NAME"),
        device=printer_uri,
        filename=os.getenv("CUPS_PRINTER_PPD_FILE_LOCATION")
    )

    connection.enablePrinter(os.getenv("CUPS_PRINTER_NAME"))
    connection.acceptJobs(os.getenv("CUPS_PRINTER_NAME"))

    # connection.disablePrinter(os.getenv("CUPS_PRINTER_NAME"))  # REMOVE LATER
