import asyncio
import sys
from aiogram import Bot, Dispatcher
from handlers import get_router
from scheduler import schedule_weekly_report
from db import init_db
from config import API_TOKEN
from logger import logger


bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher()


async def main() -> None:
    await init_db()
    asyncio.create_task(schedule_weekly_report(bot))

    dispatcher.include_router(get_router())

    logger.info('✅ Бот запущен!')
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning('⚠️ Бот остановлен!')
    except Exception as e:
        logger.error(f'❌ Ошибка: {e}', exc_info=True)
        sys.exit(1)
