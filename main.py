import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN

from database import engine
from models import Base

from handlers.menu import get_menu_handlers
from handlers.client import get_handlers


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


logger = logging.getLogger(__name__)


# Создание таблиц
Base.metadata.create_all(
    bind=engine
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        "🔥 KOD 168 CRM\n\n"
        "Добро пожаловать!\n\n"
        "Открыть меню:\n"
        "/menu"
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "Ошибка:",
        exc_info=context.error
    )


def main():

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # Ошибки
    application.add_error_handler(
        error_handler
    )


    # Старт
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # CRM ПЕРВЫМ
    for handler in get_handlers():
        application.add_handler(handler)


    # МЕНЮ ПОСЛЕДНИМ
    for handler in get_menu_handlers():
        application.add_handler(handler)


    logger.info(
        "🔥 KOD 168 CRM ONLINE"
    )


    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()