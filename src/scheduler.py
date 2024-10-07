import asyncio
from datetime import datetime, timedelta
from db import get_async_session, User
from sqlalchemy.future import select
from languages import LANGUAGES, EXCLUDED_LANGUAGES
from logger import logger
from fetch import fetch_wakatime_data, fetch_wakatime_user


EXCLUDE_LANGUAGES_ENABLED = True


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}ч {minutes}мин" if hours else f"{minutes}мин"


async def send_weekly_report(user_id, chat_id, bot, reply_to_message_id):
    async for session in get_async_session():
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalars().first()

        if user and user.wakatime_api_key:
            nickname = await fetch_wakatime_user(user.wakatime_api_key)
            data = await fetch_wakatime_data(user.wakatime_api_key)
            if data and data.get("data"):
                total_seconds = 0
                language_times = {}

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

                        total_seconds += seconds

                sorted_languages = sorted(
                    language_times.items(),
                    key=lambda item: item[1]["total_seconds"],
                    reverse=True,
                )[:15]

                report_lines = []
                for name, details in sorted_languages:
                    hours = details["total_seconds"] // 3600
                    minutes = (details["total_seconds"] % 3600) // 60
                    report_lines.append(
                        f"{details['emoji']} {name}: {int(hours)}ч {int(minutes)}мин"
                    )

                total_hours = total_seconds // 3600
                total_minutes = (total_seconds % 3600) // 60
                total_time = f"{int(total_hours)}ч {int(total_minutes)}мин"

                report = (
                    f"📝 *Отчет по времени кодинга за последние 7 дней для @{nickname}:*\n\n"
                    + "\n".join(report_lines)
                    + f"\n\n⏳ *Общее время*: {total_time}"
                )

                try:
                    await bot.send_message(
                        chat_id,
                        report,
                        parse_mode="Markdown",
                        reply_to_message_id=reply_to_message_id,
                    )
                    logger.info(
                        f"✅ Отправлен отчёт wakatime пользователю @{nickname} (telegram: {user_id})"
                    )
                except Exception as e:
                    logger.error(f"❌ Ошибка при отправке сообщения: {e}")
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
                await send_weekly_report(user_id, bot)
