
"""
Centralized logging setup for Model Manager modules.
Configures file and stream handlers, log rotation, and supports environment-based log level control.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.environ.get('MMANAGER_LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger("mmanager")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')

if not logger.hasHandlers():
    file_handler = RotatingFileHandler('mmanager_log.log', maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)