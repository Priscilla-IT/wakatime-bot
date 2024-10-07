#!/bin/bash

SESSION_NAME="wakatime_bot"

if [ "$1" == "--stop" ]; then
    if screen -list | grep -q "$SESSION_NAME"; then
        screen -S "$SESSION_NAME" -X quit
        echo "🛑 Бот остановлен."
    else
        echo "❌ Не найдено запущенной сессии для '$SESSION_NAME'."
    fi
    exit 0
fi

if screen -list | grep -q "$SESSION_NAME"; then
    echo "⚠️ Сессия '$SESSION_NAME' уже существует. Пожалуйста, завершите её или выберите другое имя."
    exit 1
fi

screen -S "$SESSION_NAME" -d -m uv run src/bot.py

if [ $? -eq 0 ]; then
    echo "✅ Бот запущен в фоновом режиме в сессии screen '$SESSION_NAME'."
else
    echo "❌ Не удалось запустить бота."
    exit 1
fi
