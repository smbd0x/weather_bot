import logging
from logging.handlers import RotatingFileHandler
import sys


def setup_logger(name: str, level=logging.INFO, logfile=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | user_id=%(user_id)s | %(message)s"
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if logfile:
        fh = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    class ContextFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, "user_id"):
                record.user_id = "-"
            return True

    logger.addFilter(ContextFilter())

    return logger


bot_logger = setup_logger("bot", level=logging.DEBUG, logfile="logs/bot.log")
service_logger = setup_logger("services", level=logging.INFO, logfile="logs/services.log")
repo_logger = setup_logger("repositories", level=logging.INFO, logfile="logs/repositories.log")
