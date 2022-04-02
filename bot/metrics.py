import socket

from prometheus_client import Counter, Gauge

import config


async def is_port_open(ip: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)

    try:
        s.connect((ip, port))
        return True
    except:
        return False


async def is_connected_to_printer_update():
    is_printer_available = await is_port_open(config.PRINTER_IP, 9100)
    Metrics.is_connected.set(int(is_printer_available))


class Metrics:
    start_time = Gauge("start_time", "Start time")
    is_connected = Gauge("printer_connected", "Is connected to printer")

    messages = Counter("messages", "Total messages received")
    message_handler_functions = Counter("message_handler_functions", "Raised functions", ["name"])
    message_handler_commands = Counter("message_handler_commands", "Command names", ["name"])

    callback_queries = Counter("callback_queries", "Total callback queries processed")
    callback_queries_functions = Counter("callback_queries_functions", "Raised functions", ["name"])

    logs = Counter("logs", "log records", ["name", "level"])

    printing = Counter("printing", "Success printing file", ["type"])
    printing.labels("requests")
    printing.labels("pages")
    printing.labels("copies")
    printing.labels("total")

    print_file_formats = Counter("print_files_formats", "Formats of files sent to printer", ["format"])

    scanning = Counter("scanning", "Success scanning", ["type"])
    scanning.labels("requests")
