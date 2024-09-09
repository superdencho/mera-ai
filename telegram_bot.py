from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from qa_bot import answer_question


# Обработчик сообщений Telegram
async def handle_message(update: Update, context):
    if update.message and update.message.text:
        user_question = update.message.text
        response = answer_question(
            context.bot_data["vector_store"],
            user_question,
            context.bot_data["openai_api_key"],
        )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение.")


def start_bot(telegram_bot_token, vector_store, openai_api_key):
    app = ApplicationBuilder().token(telegram_bot_token).build()

    # Сохраняем индекс и API ключ в контексте бота
    app.bot_data["vector_store"] = vector_store
    app.bot_data["openai_api_key"] = openai_api_key

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(message_handler)

    print("Бот запущен и готов отвечать на вопросы!")
    app.run_polling()
