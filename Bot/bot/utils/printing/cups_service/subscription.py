import cups
from cups_notify import Subscriber
import os


def create_subscription(conn: cups.Connection):
    sub = Subscriber(conn, local_address=os.getenv("BOT_CUPS_SUBSCRIPTION_LOCAL_ADDRESS"))

    return sub


