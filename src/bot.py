import asyncio
from aiogram import Bot, Dispatcher
from handlers import get_router
from scheduler import schedule_weekly_report
from db import init_db
from config import API_TOKEN
from logger import logger


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


async def main() -> None:
    await init_db()
    asyncio.create_task(schedule_weekly_report(bot))

    dp.include_router(get_router())

    logger.info("✅ Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warn("⚠️ Бот остановлен!")
