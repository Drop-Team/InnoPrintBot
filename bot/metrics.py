from prometheus_client import Counter, Gauge


class Metrics:
    start_time = Gauge("start_time", "Start time")

    users = Gauge("users_total", "Total users count", ["state"])

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
