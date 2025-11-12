import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FORMAT, LOGS_DIR

def setup_logger(name, log_file=None, level=None):
    if level is None:
        level = getattr(logging, LOG_LEVEL)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOGS_DIR / log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def get_logger(name):
    return logging.getLogger(name)
