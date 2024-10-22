import os
from dotenv import load_dotenv
from logger import logger


def load_api_token() -> str:
    load_dotenv()
    api_token = os.getenv('BOT_API_TOKEN')

    if not api_token:
        logger.error(
            "❌ Ошибка: переменная окружения 'BOT_API_TOKEN' не установлена."
        )
        raise ValueError(
            "❌ Ошибка: переменная окружения 'BOT_API_TOKEN' не установлена."
        )

    return api_token


API_TOKEN = load_api_token()
