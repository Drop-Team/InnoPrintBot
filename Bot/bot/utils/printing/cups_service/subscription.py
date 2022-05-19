import cups
from cups_notify import Subscriber


def create_subscription(conn: cups.Connection):
    sub = Subscriber(conn)

    return sub


