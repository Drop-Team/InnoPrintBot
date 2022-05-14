import logging

from bot.utils.metrics import metrics


class LogsHandler(logging.Handler):
    def emit(self, record):
        metrics.logs.labels(record.name, record.levelname).inc()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,
    filename="bot.log"
)
logger = logging.getLogger("bot")

logging.getLogger().addHandler(LogsHandler())
