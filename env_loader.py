import os
from dotenv import load_dotenv
from pydantic import SecretStr

# Загружаем переменные окружения
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка наличия API-ключей
if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "Необходимо установить ключи OPENAI_API_KEY и TELEGRAM_BOT_TOKEN в .env файле"
    )

openai_api_key = SecretStr(OPENAI_API_KEY)
