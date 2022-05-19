import os
import socket

from .metrics import printer_available


def is_port_open(ip: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)

    # noinspection PyBroadException
    try:
        s.connect((ip, port))
        return True
    except Exception as e:
        return False


def is_printer_available_update():
    is_printer_available = is_port_open(os.getenv("PRINTER_HOST"), int(os.getenv("CUPS_PRINTER_PORT")))
    printer_available.set(int(is_printer_available))
