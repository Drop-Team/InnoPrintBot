#!/usr/bin/env python
import os

import dotenv
from prometheus_client import start_http_server


def main():
    dotenv.load_dotenv("../.env")

    start_http_server(int(os.getenv("PROMETHEUS_PORT")))

    import bot
    bot.start()


if __name__ == '__main__':
    main()
