from .connection import create_connection
from .subscription import create_subscription

cups_connection = create_connection()
cups_subscription = create_subscription(cups_connection)
