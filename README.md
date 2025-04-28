# Telegram Expense Bot

Простой Telegram-бот для расчёта расходов.

## Запуск локально

1. Установите зависимости:
   pip install -r requirements.txt

2. Запустите бота:
   python bot.py

## Деплой на Render

- Создайте новый Web Service на Render.
- Укажите команду запуска: python bot.py
- В переменных окружения добавьте TELEGRAM_BOT_TOKEN (или пропишите токен прямо в коде, как сейчас).
