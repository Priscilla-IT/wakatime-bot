from datetime import datetime
from loguru import logger


def now():
    return datetime.now().strftime("%d-%m-%Y")


logger.add(
    f"logs/{now()}_miyoko.log",
    rotation="00:00",
    retention="14 days",
    level="INFO",
    format="{time:DD/MM/YYYY HH:mm:ss} | {level} | {message}",
)

logger.add(
    f"logs/{now()}_miyoko.log",
    rotation="00:00",
    retention="14 days",
    level="WARNING",
    format="{time:DD/MM/YYYY HH:mm:ss} | {level} | {message}",
)

logger.add(
    f"logs/{now()}_miyoko.log",
    rotation="00:00",
    retention="14 days",
    level="ERROR",
    format="{time:DD/MM/YYYY HH:mm:ss} | {level} | {message}",
)
