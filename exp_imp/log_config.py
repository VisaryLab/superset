import sys
from logging.handlers import QueueHandler
import logging
import datetime

def formatTime(self, record, datefmt=None):
    return datetime.datetime.fromtimestamp(record.created).astimezone().isoformat(timespec='milliseconds')

def logger_config(logger):
    streamHandler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - [%(threadName)s] [(%(thread)d)] [%(name)s] [%(levelname)s]  %(message)s')
    logging.Formatter.formatTime = formatTime

    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    level = getattr(logging, "INFO")
    logger.setLevel(level)
    logger.propagate = False