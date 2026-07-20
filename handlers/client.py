from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from database import get_db
from models import Client


NAME, PHONE, HAIRCUT, NOTES = range(4)


async def add_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "👤 Введите имя клиента:"
    )

    return NAME


async def get_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📱 Введите телефон клиента:"
    )

    return PHONE


async def get_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "✂️ Какая любимая стрижка?"
    )

    return HAIRCUT


async def get_haircut(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["haircut"] = update.message.text

    await update.message.reply_text(
        "📝 Добавьте заметки мастера:"
    )

    return NOTES


async def get_notes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["notes"] = update.message.text

    db = get_db()

    client = Client(
        name=context.user_data["name"],
        phone=context.user_data["phone"],
        haircut=context.user_data["haircut"],
        notes=context.user_data["notes"]
    )

    db.add(client)
    db.commit()
    db.close()

    await update.message.reply_text(
        "✅ Клиент сохранён в CRM КОД 168"
    )

    return ConversationHandler.END


async def clients(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    db = get_db()

    users = db.query(Client).all()

    if not users:

        await update.message.reply_text(
            "👥 Клиентов пока нет."
        )

        db.close()
        return


    text = "👥 Клиенты КОД 168:\n\n"

    for number, user in enumerate(users, start=1):

        text += f"{number}. {user.name}\n"


    db.close()

    await update.message.reply_text(
        text
    )


def get_handlers():

    return [

        ConversationHandler(
            entry_points=[
                CommandHandler(
                    "add",
                    add_start
                )
            ],

            states={

                NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_name
                    )
                ],

                PHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_phone
                    )
                ],

                HAIRCUT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_haircut
                    )
                ],

                NOTES: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        get_notes
                    )
                ]

            },

            fallbacks=[]
        ),

        CommandHandler(
            "clients",
            clients
        )
    ]