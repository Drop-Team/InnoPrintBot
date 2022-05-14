from prometheus_client import Counter, Gauge

start_time = Gauge(
    "start_time", "The time when the bot was started"
)


message_handlers = Counter(
    "message_handlers", "Updates when the user sends a message to the bot", ["handler", "command"]
)
callback_query_handlers = Counter(
    "callback_query_handlers", "Updates when the user sends a callback query", ["handler", "data"]
)


logs = Counter(
    "logs", "log records", ["name", "level"]
)


printing = Counter(
    "printing", "Confirmed print jobs by options", ["option"]
)
printing.labels("jobs")
printing.labels("pages_total")

print_files_extensions = Counter(
    "print_files_extensions", "Extensions of files submitted for printing", ["extension"]
)


scanning = Counter(
    "scanning", "Confirmed scan jobs", ["type"]
)
scanning.labels("default")
scanning.labels("multiscan")
