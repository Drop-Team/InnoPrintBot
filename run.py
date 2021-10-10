#!/usr/bin/env python
import bot
from prometheus_client import start_http_server


def main():
    start_http_server(8000)
    bot.start()


if __name__ == '__main__':
    main()
