from bot.users import users


def check_not_command(msg):
    if msg.text:
        return not msg.text.startswith("/")
    if msg.caption:
        return not msg.caption.startswith("/")
    return True


class MessageHandler:
    def __init__(self, func, custom_filters, commands, content_types, user_state, text, text_blacklist, not_command):
        self.func = func
        self.custom_filters = list(custom_filters)
        self.commands = commands
        self.content_types = ["any"] if content_types is None else content_types
        if user_state is not None:
            self.custom_filters.append(lambda msg: users[msg.from_user.id].state == user_state)
        if text is not None:
            self.custom_filters.append(lambda msg: msg.text == text)
        if text_blacklist is not None:
            self.custom_filters.append(lambda msg: msg.text not in text_blacklist)
        if not_command == True:
            self.custom_filters.append(check_not_command)


def add_message_handler(*custom_filters, commands=None, content_types=None,
                        user_state=None, text=None, text_blacklist=None, not_command=False):
    """decorator for message handlers"""

    def decorator(handler_func):
        message_handlers.append(MessageHandler(handler_func, custom_filters, commands, content_types, user_state, text,
                                               text_blacklist, not_command))
        return handler_func

    return decorator


def register_message_handlers(dp):
    """register all message handlers in dispatcher"""
    for handler in message_handlers:
        dp.register_message_handler(handler.func,
                                    *handler.custom_filters,
                                    commands=handler.commands,
                                    content_types=handler.content_types)


message_handlers = []
