from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)

from database import get_db
from models import Client


async def add_client(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    args = context.args

    if not args:
        await update.message.reply_text(
            "Используй:\n"
            "/add Имя клиента"
        )
        return

    name = " ".join(args)

    db = get_db()

    client = Client(
        name=name
    )

    db.add(client)
    db.commit()

    db.close()

    await update.message.reply_text(
        f"✅ Клиент добавлен:\n{name}"
    )


async def clients(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    db = get_db()

    users = db.query(Client).all()

    if not users:
        await update.message.reply_text(
            "Клиентов пока нет."
        )
        db.close()
        return

    text = "👤 Клиенты:\n\n"

    for user in users:
        text += f"• {user.name}\n"

    db.close()

    await update.message.reply_text(
        text
    )


def get_handlers():

    return [
        CommandHandler(
            "add",
            add_client
        ),

        CommandHandler(
            "clients",
            clients
        )
    ]
