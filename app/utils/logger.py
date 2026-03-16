import sys
from loguru import logger
from config.settings import settings


def setup_logger():
    logger.remove()

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(sys.stdout, format=fmt,
               level="DEBUG" if settings.debug else "INFO", colorize=True)

    logger.add("logs/recommandish_{time:YYYY-MM-DD}.log",
               format=fmt, level="INFO",
               rotation="10 MB", retention="7 days")

    return logger


logger = setup_logger()