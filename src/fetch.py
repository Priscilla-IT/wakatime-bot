import aiohttp
from datetime import datetime, timedelta
from logger import logger


async def fetch_wakatime_user(api_key):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Basic {api_key}:"}

        async with session.get(
            "https://wakatime.com/api/v1/users/current", headers=headers
        ) as response:
            if response.status == 200:
                user_data = await response.json()
                return user_data.get("data", {}).get("username", "")
            else:
                logger.error(
                    f"❌ Ошибка при получении данных о пользователе: {response.status}"
                )
                return None


async def fetch_wakatime_data(api_key):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Basic {api_key}:"}

        end_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
        start_of_week = end_of_week - timedelta(days=6)

        async with session.get(
            f"https://wakatime.com/api/v1/users/current/summaries?start={start_of_week}&end={end_of_week}",
            headers=headers,
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.error(
                    f"❌ Ошибка при получении данных: {response.status}"
                )
                return None
