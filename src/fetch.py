import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from logger import logger


async def make_wakatime_request(
    url: str, api_key: str
) -> Optional[Dict[str, Any]]:
    """Вспомогательная функция для выполнения GET запросов к API WakaTime."""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Basic {api_key}:"}

        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()  # Возврат JSON
            else:
                logger.error(
                    f"❌ Ошибка при получении данных с {url}: {response.status}"
                )
                return None


async def fetch_wakatime_user(api_key: str) -> Optional[str]:
    """Получаем имя пользователя WakaTime текущего пользователя."""
    url = "https://wakatime.com/api/v1/users/current"
    user_data = await make_wakatime_request(url, api_key)

    if user_data:
        return user_data.get("data", {}).get(
            "username", ""
        )  # Возврат имя пользователя

    return None


def week() -> tuple[datetime, datetime]:
    """Вычисляем начало и конец текущей недели с учетом смещения на 1 день."""
    today = datetime.now()
    offset = timedelta(days=1)
    end_of_week = today - timedelta(days=today.weekday()) + offset
    start_of_week = end_of_week - timedelta(days=6)

    return start_of_week, end_of_week


async def fetch_wakatime_data(api_key: str) -> Optional[Dict[str, Any]]:
    """Получаем данные WakaTime для текущего пользователя за текущую неделю."""
    start_of_week, end_of_week = week()
    url = (
        f"https://wakatime.com/api/v1/users/current/summaries"
        f"?start={start_of_week}&end={end_of_week}"
    )
    return await make_wakatime_request(url, api_key)
