#!/usr/bin/env python
import bot
from prometheus_client import start_http_server
import config


def main():
    start_http_server(config.PROMETHEUS_PORT)
    bot.start()


if __name__ == '__main__':
    main()
