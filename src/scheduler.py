import asyncio
from datetime import datetime, timedelta
from db import get_async_session, User
from sqlalchemy.future import select
from languages import LANGUAGES, EXCLUDED_LANGUAGES
from logger import logger
from fetch import fetch_wakatime_data, fetch_wakatime_user, week
from aiohttp.client_exceptions import (
    ClientConnectorError,
)
from aiogram.exceptions import TelegramNetworkError


EXCLUDE_LANGUAGES_ENABLED = True


def format_time(seconds):
    hours, minutes = divmod(int(seconds // 60), 60)
    return f"{hours}ч {minutes}мин" if hours else f"{minutes}мин"


async def send_weekly_report(user_id, chat_id, bot, reply_to_message_id):
    async for session in get_async_session():
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalars().first()

        if user and user.wakatime_api_key:
            nickname = await fetch_wakatime_user(user.wakatime_api_key)
            try:
                data = await fetch_wakatime_data(user.wakatime_api_key)
            except ClientConnectorError as e:
                logger.error(f"❌ Ошибка соединения с Wakatime: {e}")
                return

            if data and data.get("data"):
                language_times = {}
                total_seconds = sum(
                    (
                        language["total_seconds"]
                        for day in data["data"]
                        for language in day["languages"]
                        if not (
                            EXCLUDE_LANGUAGES_ENABLED
                            and language["name"] in EXCLUDED_LANGUAGES
                        )
                    )
                )

                for day in data["data"]:
                    for language in day["languages"]:
                        name = language["name"]
                        seconds = language["total_seconds"]

                        if (
                            EXCLUDE_LANGUAGES_ENABLED
                            and name in EXCLUDED_LANGUAGES
                        ):
                            continue

                        if name in language_times:
                            language_times[name]["total_seconds"] += seconds
                        else:
                            language_times[name] = {
                                "total_seconds": seconds,
                                "emoji": LANGUAGES.get(name, "💻"),
                            }

                sorted_languages = sorted(
                    language_times.items(),
                    key=lambda item: item[1]["total_seconds"],
                    reverse=True,
                )[:15]

                report_lines = [
                    f"{details['emoji']} *{name}*: {format_time(details['total_seconds'])}"
                    for name, details in sorted_languages
                ]

                start, end = week()

                start_date = start.strftime("%d/%m/%Y")
                end_date = end.strftime("%d/%m/%Y")

                report = (
                    f"📝 *Отчет за последние 7 дней для @{nickname}:*\n\n"
                    + "\n".join(report_lines)
                    + f"\n\n⏳ *Общее время*: {format_time(total_seconds)}"
                    + f"\n📅 *Период* от {start_date} до {end_date}."
                )

                retry_attempts = 3  # Number of retry attempts
                for attempt in range(retry_attempts):
                    try:
                        await bot.send_message(
                            chat_id,
                            report,
                            parse_mode="Markdown",
                            reply_to_message_id=reply_to_message_id,
                        )
                        logger.info(
                            f"✅ Отправлен отчёт Wakatime пользователю @{nickname} (telegram: {user_id})"
                        )
                        break  # Exit the loop on successful send
                    except TelegramNetworkError as e:
                        logger.error(f"❌ Ошибка сети Telegram: {e}")
                        if attempt < retry_attempts - 1:
                            await asyncio.sleep(2**attempt)
                    except Exception as e:
                        logger.error(f"❌ Ошибка при отправке сообщения: {e}")
                        break
            else:
                await bot.send_message(
                    chat_id, "❌ Нет данных о времени, проведенном в коде."
                )
        else:
            await bot.send_message(
                chat_id, "❌ Ошибка: не найден API ключ Wakatime."
            )


async def schedule_weekly_report(bot):
    while True:
        now = datetime.now()
        next_run = now.replace(hour=12, minute=0, second=0, microsecond=0)

        if next_run < now:
            next_run += timedelta(days=1)

        await asyncio.sleep((next_run - now).total_seconds())

        async for session in get_async_session():
            result = await session.execute(select(User.user_id))
            user_ids = result.scalars().all()

            for user_id in user_ids:
                ## chat_id = 123456
                await send_weekly_report(user_id, bot)
