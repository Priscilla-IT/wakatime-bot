from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, inspect
from dotenv import load_dotenv
from logger import logger


load_dotenv()


DATABASE_URL = 'sqlite+aiosqlite:///./users.db'


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    wakatime_api_key = Column(String, nullable=False)


async_engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    try:
        async with async_engine.begin() as conn:
            if not await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).has_table('users')
            ):
                await conn.run_sync(Base.metadata.create_all)
                logger.info('ℹ️ База данных и таблицы успешно созданы.')
            else:
                logger.info(
                    '✅ Таблицы уже существуют, база данных не перезаписана.'
                )
    except Exception as e:
        logger.error(f'❌ Ошибка инициализации базы данных: {e}')


async def get_async_session() -> AsyncSession:  # type: ignore
    try:
        async with async_session() as session:
            yield session
    except Exception as e:
        logger.error(f'❌ Ошибка при получении асинхронной сессии: {e}')
