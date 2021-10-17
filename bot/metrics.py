from prometheus_client import Counter, Gauge


class Metrics:
    users = Gauge("users_total", "users who confirmed email", ["state"])

    errors = Counter("errors", "Errors count")

    start_command = Counter("start_command", "Using /start command")

    printing = Counter("printing", "Success printing file", ["type"])
    printing.labels("requests")
    printing.labels("pages")
    printing.labels("copies")
    printing.labels("total")

    print_file_formats = Counter("print_files_formats", "Formats of files sent to printer", ["format"])

    scanning = Counter("scanning", "Success scanning", ["type"])
    scanning.labels("requests")

    problem = Counter("problem", "Using problems commands", ["type"])
    problem.labels("print")
    problem.labels("scan")
