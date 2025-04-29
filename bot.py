import os
import sys
import requests
import time

# Разрешаем запуск только на Render
if not os.environ.get("RENDER"):
    print("❌ Этот бот можно запускать только на Render.com!")
    sys.exit(1)

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Настройка логирования для отслеживания ошибок
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost")

CATEGORY, COST, TIMES = range(3)

def keep_alive():
    """Функция для поддержания сервиса активным"""
    while True:
        try:
            response = requests.get(RENDER_URL)
            logger.info(f"Keep-alive ping sent. Status: {response.status_code}")
            # Спим 14 минут (840 секунд)
            time.sleep(840)
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")
            # При ошибке ждем минуту и пробуем снова
            time.sleep(60)

def run_dummy_server():
    """Запуск простого HTTP-сервера для Render"""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Привет! Я помогу посчитать твои расходы.\n\n"
            "Напиши /add чтобы начать."
        )
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("На что ты часто тратишь деньги?")
        return CATEGORY
    except Exception as e:
        logger.error(f"Error in add handler: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['category'] = update.message.text
        await update.message.reply_text("Сколько стоит один раз (тг)?")
        return COST
    except Exception as e:
        logger.error(f"Error in category handler: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['cost'] = int(update.message.text)
        await update.message.reply_text("Сколько раз в месяц?")
        return TIMES
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return COST
    except Exception as e:
        logger.error(f"Error in cost handler: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

async def times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        times = int(update.message.text)
        category = context.user_data['category']
        cost = context.user_data['cost']
        monthly = cost * times
        yearly = monthly * 12
        msg = f"Ты тратишь {monthly} тг в месяц и {yearly} тг в год на {category}."
        if monthly > 20000:
            msg += "\nСовет: попробуй сократить на 2 раза в неделю — экономия будет ощутимой!"
        else:
            msg += "\nТы хорошо контролируешь свои расходы!"
        await update.message.reply_text(msg)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return TIMES
    except Exception as e:
        logger.error(f"Error in times handler: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
    try:
        # Запускаем поток для поддержания сервиса активным
        threading.Thread(target=keep_alive, daemon=True).start()
        logger.info("Keep-alive thread started")

        # Запускаем dummy HTTP сервер для Render
        threading.Thread(target=run_dummy_server, daemon=True).start()
        logger.info("Dummy HTTP server started")

        app = ApplicationBuilder().token(TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("add", add)],
            states={
                CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
                COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost)],
                TIMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, times)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        app.add_handler(CommandHandler("start", start))
        app.add_handler(conv_handler)

        logger.info("Bot started")
        app.run_polling()
    except Exception as e:
        logger.error(f"Critical error in main: {e}")

if __name__ == "__main__":
    main()
