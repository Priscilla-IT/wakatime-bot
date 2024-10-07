from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.future import select
from db import User, get_async_session
from scheduler import send_weekly_report


router = Router()
user_api_key_requests = {}


@router.message(Command("api_key"))
async def api_key_command(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "ℹ️ Используйте команду /api_key в личных сообщениях.",
            reply_to_message_id=message.message_id,
        )
        return
    await message.reply(
        "ℹ️ Введите ваш WakaTime API ключ:",
        reply_to_message_id=message.message_id,
    )
    user_api_key_requests[message.from_user.id] = True


@router.message(Command("report"))
async def report_command(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    async for session in get_async_session():
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalars().first()

        if user and user.wakatime_api_key:
            await send_weekly_report(
                user_id,
                chat_id,
                message.bot,
                message.message_id,
            )
        else:
            await message.reply(
                "ℹ️ У вас нет сохраненного API ключа.\nИспользуйте команду /api_key.",
                reply_to_message_id=message.message_id,
            )


@router.message(Command("wakatime"))
async def help_command(message: Message):
    help_text = (
        "ℹ️ Доступные команды:\n"
        "/report - Получить отчет по времени кодинга.\n"
        "/api_key - Установить ваш WakaTime API ключ (вызывается в личных сообщениях)."
    )
    await message.reply(help_text, reply_to_message_id=message.message_id)


@router.message()
async def handle_api_key_input(message: Message):
    user_id = message.from_user.id

    if message.chat.type == "private" and user_id in user_api_key_requests:
        api_key = message.text.strip()
        async for session in get_async_session():
            user = await session.get(User, user_id)
            if user:
                user.wakatime_api_key = api_key
            else:
                user = User(user_id=user_id, wakatime_api_key=api_key)
                session.add(user)

            await session.commit()

        await message.reply(
            "✅ API ключ обновлен!", reply_to_message_id=message.message_id
        )
        del user_api_key_requests[user_id]


def get_router():
    return router
