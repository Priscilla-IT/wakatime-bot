import os
from dotenv import load_dotenv
from logger import logger


load_dotenv()


API_TOKEN = os.getenv("BOT_API_TOKEN")

if not all([API_TOKEN]):
    logger.error(
        "❌ Ошибка: не все необходимые переменные окружения установлены."
    )
    raise ValueError(
        "❌ Ошибка: не все необходимые переменные окружения установлены."
    )
