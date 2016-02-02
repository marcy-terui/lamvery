# -*- coding: utf-8 -*-

import logging
import sys
from termcolor import colored

logger = None


class ColoredStreamHandler(logging.StreamHandler):

    def format(self, record):
        message = super(ColoredStreamHandler, self).format(record)
        if record.levelno == logging.INFO:
            message = colored(message, 'green')
        elif record.levelno == logging.WARN:
            message = colored(message, 'yellow')
        elif record.levelno == logging.ERROR:
            message = colored(message, 'red')
        return message


def get_logger(name):
    global logger
    if logger is None:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = ColoredStreamHandler(stream=sys.stderr)
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter('%(name)s: %(message)s'))
        logger.removeHandler(handler)
        logger.addHandler(handler)
    return logger
