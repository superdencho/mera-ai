import os
from env_loader import openai_api_key, TELEGRAM_BOT_TOKEN
from pdf_reader import extract_texts_from_folder
from telegram_bot import start_bot
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


from langchain.text_splitter import RecursiveCharacterTextSplitter


# Функция для разделения текста на блоки
def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks


# Создание индекса на основе документов
def create_index(chunks, openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store


if __name__ == "__main__":
    # Путь к папке с PDF-документами
    folder_path = os.path.expanduser("~/Documents")

    # Извлечение текста из всех PDF-файлов в папке
    pdf_text = extract_texts_from_folder(folder_path)

    # Разделение текста на блоки
    chunks = split_text(pdf_text)

    # Создание векторного индекса
    vector_store = create_index(chunks, openai_api_key.get_secret_value())

    # Запуск Telegram-бота
    start_bot(TELEGRAM_BOT_TOKEN, vector_store, openai_api_key.get_secret_value())
