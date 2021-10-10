import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO,
    # filename="bot.log"
)
logger = logging.getLogger(__name__)
