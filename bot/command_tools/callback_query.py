from bot.logger import logger
from bot.metrics import Metrics


def get_new_function(old_function):
    def new_function(callback_query):
        log_msg = f"{callback_query.from_user.mention} ({callback_query.from_user.id}) pressed button, " \
                  f"raised function '{old_function.__name__}'"
        logger.info(log_msg)

        Metrics.callback_queries.inc()
        Metrics.callback_queries_functions.labels(f"{old_function.__name__}").inc()
        return old_function(callback_query)

    return new_function


class CallbackQuery:
    def __init__(self, func, custom_filters, callback_data):
        self.func = get_new_function(func)
        self.custom_filters = list(custom_filters)
        if callback_data is not None:
            self.custom_filters.append(lambda callback: callback.data == callback_data)


def add_callback_query(*custom_filters, callback_data=None):
    """decorator for callback query"""

    def decorator(handler_func):
        callback_queries.append(CallbackQuery(handler_func, custom_filters, callback_data))
        return handler_func

    return decorator


def register_callback_queries(dp):
    """register all callback queries in dispatcher"""
    for handler in callback_queries:
        dp.register_callback_query_handler(handler.func,
                                           *handler.custom_filters)


callback_queries = []
