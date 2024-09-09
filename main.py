import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI
from pydantic import SecretStr
from langchain.chains import VectorDBQA
from PyPDF2 import PdfReader

# Загружаем переменные окружения
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка наличия API-ключей
if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "Необходимо установить ключи OPENAI_API_KEY и TELEGRAM_BOT_TOKEN в .env файле"
    )

# Оборачиваем API-ключ в SecretStr
openai_api_key = SecretStr(OPENAI_API_KEY)

# Используем OpenAI API (нужно извлечь строковое значение ключа через get_secret_value())
openai = OpenAI(api_key=openai_api_key.get_secret_value())  # type: ignore


# Чтение PDF-файла и извлечение текста
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


# Чтение всех PDF-файлов в папке ~/Documents
def extract_texts_from_folder():
    folder_path = os.path.expanduser("~/Documents")

    all_texts = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            all_texts += extract_text_from_pdf(pdf_path) + "\n"
            print(f"Извлечен текст из файла: {filename}")
    return all_texts


# Функция для разделения текста на блоки
def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks


# Создание индекса на основе документов
def create_index(chunks):
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY
    )  # Передаем API ключ напрямую
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store


# Ответ на вопрос на основе индекса
def answer_question(vector_store, question):
    llm = OpenAI(
        api_key=openai_api_key.get_secret_value()
    )  # Извлекаем значение API ключа
    qa = VectorDBQA.from_chain_type(llm=llm, vectorstore=vector_store)
    response = qa.run(question)
    if not response:
        return "Извините, я не могу найти ответ на этот вопрос."
    return response


# Обработчик сообщений Telegram
async def handle_message(update: Update, context):
    # Проверяем, что сообщение не пустое и что это текстовое сообщение
    if update.message and update.message.text:
        user_question = update.message.text
        response = answer_question(
            vector_store, user_question
        )  # Используем наш индекс и вопрос
        await update.message.reply_text(response)
    elif update.message:
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение.")


# Основной код для запуска Telegram-бота
if __name__ == "__main__":
    # Путь к папке с PDF-документами
    folder_path = "path_to_your_pdf_folder"  # Укажи путь к папке с PDF

    # Извлечение текста из всех PDF-файлов в папке
    pdf_text = extract_texts_from_folder()

    # Разделение текста на блоки
    chunks = split_text(pdf_text)

    # Создание векторного индекса
    vector_store = create_index(chunks)

    # Запуск Telegram-бота с использованием переменной окружения для токена
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработка сообщений
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(message_handler)

    print("Бот запущен и готов отвечать на вопросы!")
    app.run_polling()
