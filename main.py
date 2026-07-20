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

from handlers.menu import get_menu_handlers
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
        "🔥 KOD 168 CRM BOT\n\n"
        "Нажмите /menu для открытия панели"
    )


def main():

    app = Application.builder()\
        .token(BOT_TOKEN)\
        .build()


    # СТАРТ
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # СНАЧАЛА МЕНЮ
    for handler in get_menu_handlers():
        app.add_handler(handler)


    # ПОТОМ CRM
    for handler in get_handlers():
        app.add_handler(handler)


    print(
        "🔥 KOD 168 CRM ONLINE"
    )


    app.run_polling()



if __name__ == "__main__":
    main()