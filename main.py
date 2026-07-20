import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN
from database import engine
from models import Base
from handlers.client import get_handlers


logging.basicConfig(
    level=logging.INFO
)


Base.metadata.create_all(
    bind=engine
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🔥 KOD 168 CRM BOT запущен\n\n"
        "Команды:\n"
        "/add Имя — добавить клиента"
    )


def main():

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
        "KOD 168 BOT STARTED"
    )


    app.run_polling()


if __name__ == "__main__":
    main()