class CallbackQuery:
    def __init__(self, func, custom_filters, callback_data):
        self.func = func
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
