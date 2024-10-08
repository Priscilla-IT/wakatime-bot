from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, get_async_session
from scheduler import send_weekly_report

router = Router()
user_api_key_requests: dict[int, bool] = {}


async def get_user_from_db(user_id: int, session: AsyncSession) -> User:
    """Вспомогательная функция для получения пользователя из базы данных."""
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalars().first()


async def store_api_key(
    user_id: int, api_key: str, session: AsyncSession
) -> None:
    """Вспомогательная функция для сохранения или обновления API ключа WakaTime в базе данных."""
    user = await session.get(User, user_id)
    if user:
        user.wakatime_api_key = (
            api_key  # Обновление API ключа, если пользователь уже существует
        )
    else:
        user = User(
            user_id=user_id, wakatime_api_key=api_key
        )  # Создаем нового пользователя с API ключом
        session.add(user)
    await session.commit()


@router.message(Command("wakatime"))
async def help_command(message: Message) -> None:
    """Обрабатывает команду /wakatime, показывая доступные команды."""
    help_text = (
        "ℹ️ Доступные команды:\n"
        "/get - Получить свой отчёт за последние 7 дней.\n"
        "/api - Установить ваш WakaTime API ключ (вызывается в личных сообщениях)."
    )
    await message.reply(help_text, reply_to_message_id=message.message_id)


@router.message(Command("report"))
async def report_command(message: Message) -> None:
    """Обрабатывает команду /report, отправляет недельный отчет, если доступен API ключ."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    async for session in get_async_session():
        user = await get_user_from_db(user_id, session)
        if user and user.wakatime_api_key:
            await send_weekly_report(
                user_id, chat_id, message.bot, message.message_id
            )  # Отправление отчёта, если API ключ доступен
        else:
            await message.reply(
                "ℹ️ У вас нет сохраненного API ключа.\nИспользуйте команду /api.",
                reply_to_message_id=message.message_id,
            )  # Если ключ не сохранен


@router.message(Command("api"))
async def api_key_command(message: Message) -> None:
    """Обрабатывает команду /api, запрашивает у пользователя API ключ WakaTime."""
    if message.chat.type != "private":
        await message.reply(
            "ℹ️ Используйте команду /api в личных сообщениях.",
            reply_to_message_id=message.message_id,
        )
        return
    await message.reply(
        "ℹ️ Введите ваш WakaTime API ключ:",
        reply_to_message_id=message.message_id,
    )
    user_api_key_requests[message.from_user.id] = (
        True  # Ожидаем ввод API ключа
    )


@router.message()
async def handle_api_key_input(message: Message) -> None:
    """Обрабатывает ввод API ключа пользователем в личных сообщениях."""
    user_id = message.from_user.id

    if message.chat.type == "private" and user_id in user_api_key_requests:
        api_key = message.text.strip()  # Получаем API ключ
        async for session in get_async_session():
            await store_api_key(
                user_id, api_key, session
            )  # Сохранение API ключа в базе данных

        await message.reply(
            "✅ API ключ обновлен!", reply_to_message_id=message.message_id
        )
        del user_api_key_requests[
            user_id
        ]  # Удаление пользователя из списка ожидания ключа


def get_router() -> Router:
    """Возвращает экземпляр маршрута."""
    return router
