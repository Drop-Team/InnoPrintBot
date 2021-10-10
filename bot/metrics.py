from prometheus_client import Counter, Gauge


def save_users_metrics(data):
    Metrics.users_total.set(len(data))


class Metrics:
    users_total = Gauge("authorized_users_total", "users who confirmed email")

    errors = Counter("errors", "Errors count")

    start_command = Counter("start_command", "Using /start command")

    printing = Counter("printing", "Success printing file", ["type"])
    printing.labels("requests")
    printing.labels("pages")

    print_file_formats = Counter("print_files_formats", "Formats of files sent to printer", ["format"])

    scanning = Counter("scanning", "Success scanning", ["type"])
    scanning.labels("requests")
