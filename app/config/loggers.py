import logging

logging.basicConfig(level=logging.INFO)

def get_and_set_logger(name: str, level: str = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

