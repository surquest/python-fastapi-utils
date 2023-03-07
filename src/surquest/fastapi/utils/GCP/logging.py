"""Logging Module for FastAPI Application

The main source of inspiration for this module is the following:

* https://github.com/madzak/python-json-logger/blob/master/src/pythonjsonlogger/jsonlogger.py
* https://dev.to/floflock/enable-feature-rich-logging-for-fastapi-on-google-cloud-logging-j3i
* https://github.com/python/cpython/blob/3.11/Lib/logging/__init__.py
* https://docs.python.org/3/howto/logging.html#logging-flow
* https://github.com/googleapis/python-logging/blob/a453fd8e9587e42758888649f8fb433967620e14/google/cloud/logging_v2/handlers/handlers.py#L118

"""

# import external modules
import os
import logging

# import internal modules
from .formatter import JSONFormatter


__all__ = ["Logger", "setup_logging", "DEFAULT_LOGGER_NAME"]

DEFAULT_LOGGER_NAME = os.getenv('APP_NAME', "APILogger")

Logger = logging.getLogger(DEFAULT_LOGGER_NAME)


def setup_logging(level=logging.DEBUG):
    # get default handler
    handler = logging.StreamHandler()


    if os.getenv("ENV", "").upper() != "LOCAL":
        json_formatter = JSONFormatter()
        handler.setFormatter(json_formatter)
        handler.setLevel(level)

    else:
        # set default formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)

    # set logger
    Logger.handlers = []
    Logger.addHandler(handler)
    Logger.setLevel(level)
