import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

TOKEN = "8046683823:AAHAsh3lbVcR-9pz5kOlkXezxpKdM1U9V30"

logging.basicConfig(level=logging.INFO)

CATEGORY, COST, TIMES = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу посчитать твои расходы.\n\n"
        "Напиши /add чтобы начать."
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("На что ты часто тратишь деньги?")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("Сколько стоит один раз (тг)?")
    return COST

async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['cost'] = int(update.message.text)
        await update.message.reply_text("Сколько раз в месяц?")
        return TIMES
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return COST

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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main():
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

    app.run_polling()

if __name__ == "__main__":
    main()
