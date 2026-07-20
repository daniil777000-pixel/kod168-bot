import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN


logging.basicConfig(
    level=logging.INFO
)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🔥 KOD 168 CRM BOT запущен\n\n"
        "Система готова к работе."
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

    print(
        "KOD 168 BOT STARTED"
    )

    app.run_polling()


if __name__ == "__main__":
    main()
