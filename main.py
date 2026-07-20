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
from handlers.menu import get_menu_handlers


logging.basicConfig(
    level=logging.INFO
)


# Создание таблиц базы
Base.metadata.create_all(
    bind=engine
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🔥 KOD 168 CRM BOT\n\n"
        "Добро пожаловать!\n\n"
        "Используйте меню:\n"
        "/menu"
    )


def main():

    app = Application.builder() \
        .token(BOT_TOKEN) \
        .build()


    # Старт
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # Клиенты
    for handler in get_handlers():
        app.add_handler(handler)


    # Меню
    for handler in get_menu_handlers():
        app.add_handler(handler)


    print(
        "🔥 KOD 168 CRM BOT STARTED"
    )


    app.run_polling()



if __name__ == "__main__":
    main()