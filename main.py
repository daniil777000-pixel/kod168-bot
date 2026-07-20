import logging
import threading

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from flask import Flask

from config import BOT_TOKEN
from database import engine
from models import Base
from handlers.client import get_handlers


logging.basicConfig(
    level=logging.INFO
)


# Создание базы
Base.metadata.create_all(
    bind=engine
)


# Flask для Render
web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "KOD 168 CRM BOT ONLINE 🔥"


@web_app.route("/health")
def health():
    return {
        "status": "ok",
        "project": "KOD 168 CRM"
    }


def run_web():
    web_app.run(
        host="0.0.0.0",
        port=10000
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🔥 KOD 168 CRM BOT запущен\n\n"
        "Команды:\n"
        "/add — добавить клиента\n"
        "/clients — список клиентов"
    )


def run_bot():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    for handler in get_handlers():
        app.add_handler(handler)


    print(
        "🔥 KOD 168 BOT STARTED"
    )


    app.run_polling()


def main():

    # запускаем сайт для Render
    threading.Thread(
        target=run_web
    ).start()


    # запускаем Telegram
    run_bot()


if __name__ == "__main__":
    main()